"""
routes/knowledge_base.py
------------------------
Self-service Knowledge Base and Instant Solution Deflection engine.
Features:
    * Search & browse IT solution guides
    * Instant deflection API endpoint (/kb/suggest) used by create_ticket.html
    * Mark solution as helpful counter
    * Article management (admin & support staff)
"""

from datetime import datetime

from flask import (
    Blueprint,
    flash,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)
from sqlalchemy import or_

from extensions import db
from models import Category, KnowledgeArticle
from utils import login_required

kb_bp = Blueprint("kb", __name__, url_prefix="/kb")

# Common English stop words to ignore during live suggestion tokenization
STOP_WORDS = {
    "a", "an", "the", "and", "or", "in", "on", "at", "to", "for", "with",
    "by", "about", "like", "through", "over", "before", "between", "after",
    "since", "without", "under", "within", "along", "following", "across",
    "behind", "beyond", "plus", "except", "until", "is", "am", "are", "was",
    "were", "be", "being", "been", "have", "has", "had", "do", "does", "did",
    "can", "could", "shall", "should", "will", "would", "may", "might", "must",
    "my", "me", "i", "we", "our", "you", "your", "he", "she", "it", "they",
    "this", "that", "these", "those", "not", "no", "problem", "issue", "help",
}


@kb_bp.route("/")
@login_required()
def index():
    """Browse and search knowledge base articles."""
    query = KnowledgeArticle.query
    search = request.args.get("q", "").strip()
    category_id = request.args.get("category", type=int)

    if category_id:
        query = query.filter(KnowledgeArticle.category_id == category_id)

    if search:
        like = f"%{search}%"
        query = query.filter(
            or_(
                KnowledgeArticle.title.ilike(like),
                KnowledgeArticle.keywords.ilike(like),
                KnowledgeArticle.solution.ilike(like),
            )
        )

    articles = query.order_by(KnowledgeArticle.helpful_count.desc(), KnowledgeArticle.views.desc()).all()
    categories = Category.query.order_by(Category.name).all()

    return render_template(
        "knowledge_base.html",
        articles=articles,
        categories=categories,
        search=search,
        selected_category=category_id,
    )


@kb_bp.route("/<int:article_id>")
@login_required()
def detail(article_id):
    """View a single knowledge base solution."""
    article = db.get_or_404(KnowledgeArticle, article_id)
    article.views += 1
    db.session.commit()

    related = (
        KnowledgeArticle.query.filter(
            KnowledgeArticle.category_id == article.category_id,
            KnowledgeArticle.id != article.id,
        )
        .limit(4)
        .all()
    )

    return render_template(
        "knowledge_article.html",
        article=article,
        related=related,
    )


@kb_bp.route("/<int:article_id>/helpful", methods=["POST"])
@login_required()
def mark_helpful(article_id):
    """Upvote an article when it helps solve a problem."""
    article = db.get_or_404(KnowledgeArticle, article_id)
    article.helpful_count += 1
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.is_json:
        return jsonify({"success": True, "helpful_count": article.helpful_count})

    flash("Thank you for your feedback!", "success")
    return redirect(request.referrer or url_for("kb.detail", article_id=article.id))


@kb_bp.route("/suggest")
@login_required()
def suggest():
    """
    Live ticket deflection API:
    Accepts search query string from create_ticket.html as the user types,
    and returns top matching self-service solutions as JSON.
    """
    raw_query = request.args.get("q", "").strip().lower()
    category_id = request.args.get("category_id", type=int)

    if len(raw_query) < 3:
        return jsonify({"count": 0, "articles": []})

    # Tokenize input into meaningful keywords
    words = [
        w for w in "".join(c if c.isalnum() else " " for c in raw_query).split()
        if len(w) >= 3 and w not in STOP_WORDS
    ]

    if not words:
        words = [raw_query]

    # Build SQL filter matching any relevant keyword
    conditions = []
    for word in words:
        like = f"%{word}%"
        conditions.append(KnowledgeArticle.title.ilike(like))
        conditions.append(KnowledgeArticle.keywords.ilike(like))
        conditions.append(KnowledgeArticle.solution.ilike(like))

    query = KnowledgeArticle.query.filter(or_(*conditions))

    if category_id:
        # Boost matches in the selected category or include them
        query = query.filter(
            or_(KnowledgeArticle.category_id == category_id, KnowledgeArticle.category_id.isnot(None))
        )

    matches = query.limit(5).all()

    # Score and sort matches: title match gets highest score
    def score_article(art):
        score = 0
        title_lower = art.title.lower()
        kw_lower = (art.keywords or "").lower()
        sol_lower = art.solution.lower()

        for w in words:
            if w in title_lower:
                score += 10
            if w in kw_lower:
                score += 5
            if w in sol_lower:
                score += 2
        score += art.helpful_count
        return score

    sorted_matches = sorted(matches, key=score_article, reverse=True)

    results = []
    for a in sorted_matches:
        # Clean preview snippet
        summary = a.solution.replace("\n", " ").strip()
        if len(summary) > 160:
            summary = summary[:160] + "..."

        results.append(
            {
                "id": a.id,
                "title": a.title,
                "category": a.category.name if a.category else "General",
                "summary": summary,
                "solution": a.solution,
                "helpful_count": a.helpful_count,
            }
        )

    return jsonify({"count": len(results), "articles": results})


@kb_bp.route("/new", methods=["GET", "POST"])
@login_required("admin", "support")
def create_article():
    """Add a new solution guide to the knowledge base."""
    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category_id = request.form.get("category_id", type=int)
        keywords = request.form.get("keywords", "").strip()
        solution = request.form.get("solution", "").strip()

        errors = []
        if len(title) < 5:
            errors.append("Article title must be at least 5 characters.")
        if not category_id or db.session.get(Category, category_id) is None:
            errors.append("Please choose a valid category.")
        if len(solution) < 20:
            errors.append("Please provide detailed solution steps (at least 20 characters).")

        if errors:
            for msg in errors:
                flash(msg, "danger")
            return render_template("kb_edit.html", categories=categories, article=request.form)

        article = KnowledgeArticle(
            title=title,
            category_id=category_id,
            keywords=keywords,
            solution=solution,
        )
        db.session.add(article)
        db.session.commit()

        flash(f"Article '{title}' added to Knowledge Base.", "success")
        return redirect(url_for("kb.detail", article_id=article.id))

    return render_template("kb_edit.html", categories=categories, article=None)


@kb_bp.route("/<int:article_id>/edit", methods=["GET", "POST"])
@login_required("admin", "support")
def edit_article(article_id):
    """Edit an existing knowledge base article."""
    article = db.get_or_404(KnowledgeArticle, article_id)
    categories = Category.query.order_by(Category.name).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        category_id = request.form.get("category_id", type=int)
        keywords = request.form.get("keywords", "").strip()
        solution = request.form.get("solution", "").strip()

        errors = []
        if len(title) < 5:
            errors.append("Article title must be at least 5 characters.")
        if not category_id or db.session.get(Category, category_id) is None:
            errors.append("Please choose a valid category.")
        if len(solution) < 20:
            errors.append("Please provide detailed solution steps (at least 20 characters).")

        if errors:
            for msg in errors:
                flash(msg, "danger")
            return render_template("kb_edit.html", categories=categories, article=article)

        article.title = title
        article.category_id = category_id
        article.keywords = keywords
        article.solution = solution
        db.session.commit()

        flash("Article updated successfully.", "success")
        return redirect(url_for("kb.detail", article_id=article.id))

    return render_template("kb_edit.html", categories=categories, article=article)


@kb_bp.route("/<int:article_id>/delete", methods=["POST"])
@login_required("admin")
def delete_article(article_id):
    """Admin can delete outdated or unwanted articles."""
    article = db.get_or_404(KnowledgeArticle, article_id)
    title = article.title
    db.session.delete(article)
    db.session.commit()

    flash(f"Knowledge article '{title}' deleted.", "success")
    return redirect(url_for("kb.index"))

