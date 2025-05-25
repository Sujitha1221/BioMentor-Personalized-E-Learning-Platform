from fastapi import APIRouter
from fastapi.responses import HTMLResponse
import matplotlib.pyplot as plt
import io
import base64

router = APIRouter()

def plot_to_base64(plt):
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return base64.b64encode(buf.getvalue()).decode('utf-8')

@router.get("/user/{user_id}/stats", response_class=HTMLResponse)
async def user_stats_with_charts(user_id: str):
    stats = await get_user_stats(user_id)

    if "error" in stats:
        return f"<h2>Error: {stats['error']}</h2>"

    # Bar chart: Score distribution
    plt.figure()
    x = list(stats["score_distribution"].keys())
    y = list(stats["score_distribution"].values())
    plt.bar(x, y)
    plt.title("Review Score Distribution")
    plt.xlabel("Score (0-5)")
    plt.ylabel("Count")
    score_chart = plot_to_base64(plt)

    # Pie chart: Review schedule
    plt.figure()
    labels = list(stats["review_schedule"].keys())
    sizes = list(stats["review_schedule"].values())
    plt.pie(sizes, labels=labels, autopct="%1.1f%%")
    plt.title("Upcoming Review Schedule")
    schedule_chart = plot_to_base64(plt)

    # Construct HTML
    html_content = f"""
    <h2>User Stats for {stats['username']}</h2>
    <p><strong>Total Score:</strong> {stats['total_score']}</p>
    <p><strong>Total Reviews:</strong> {stats['total_reviews']}</p>
    <p><strong>Average Score:</strong> {stats['average_score']}</p>

    <h3>Score Distribution</h3>
    <img src="data:image/png;base64,{score_chart}" />

    <h3>Review Schedule</h3>
    <img src="data:image/png;base64,{schedule_chart}" />
    """
    return HTMLResponse(content=html_content)
