
import json
from pathlib import Path

from app.database.connection import SessionLocal
from app.retrieval.search import search_similar_chunks

from app.evaluation.metrics import (
    recall_at_k,
    precision_at_k,
    reciprocal_rank,
    hit_rate_at_k,
)


BASE_DIR = Path(__file__).resolve().parents[2]

DATASET_PATH = BASE_DIR / "data" / "evaluation" / "evaluation_dataset.json"
JUDGMENTS_PATH = BASE_DIR / "data" / "evaluation" / "relevance_judgments.json"

with open(DATASET_PATH, "r", encoding="utf-8") as file:
    evaluation_dataset = json.load(file)

with open(JUDGMENTS_PATH, "r", encoding="utf-8") as file:
    relevance_data = json.load(file)

DOCUMENT_ID = relevance_data["document_id"]
K = 5

judgments_by_question = {
    judgment["question_id"]: judgment["relevant_chunk_ids"]
    for judgment in relevance_data["judgments"]
}



def run_evaluation():
    db = SessionLocal()

    try:
        results_summary = []

        for item in evaluation_dataset:
            question_id = item["id"]
            question = item["question"]

            relevant_ids = judgments_by_question[question_id]

            search_results = search_similar_chunks(
                db=db,
                question=question,
                document_id=DOCUMENT_ID,
                limit=K
            )

            retrieved_ids = [
                chunk.id
                for chunk, distance in search_results
            ]

            recall = recall_at_k(retrieved_ids, relevant_ids, K)
            precision = precision_at_k(retrieved_ids, relevant_ids, K)
            rr = reciprocal_rank(retrieved_ids, relevant_ids)
            hit_rate = hit_rate_at_k(retrieved_ids, relevant_ids, K)

            results_summary.append({
                "question_id": question_id,
                "retrieved_ids": retrieved_ids,
                "recall": recall,
                "precision": precision,
                "reciprocal_rank": rr,
                "hit_rate": hit_rate
            })

            print(f"\nQuestion : {question_id}")
            print(f"Chunks retrouvés : {retrieved_ids}")
            print(f"Chunks pertinents : {relevant_ids}")
            print(f"Recall@{K} : {recall:.3f}")
            print(f"Precision@{K} : {precision:.3f}")
            print(f"Reciprocal Rank : {rr:.3f}")
            print(f"Hit Rate@{K} : {hit_rate:.3f}")

        return results_summary

    finally:
        db.close()



def calculate_global_metrics(results):
    number_of_questions = len(results)

    if number_of_questions == 0:
        raise ValueError("The evaluation dataset is empty.")

    mean_recall = sum(
        result["recall"] for result in results
    ) / number_of_questions

    mean_precision = sum(
        result["precision"] for result in results
    ) / number_of_questions

    mean_reciprocal_rank = sum(
        result["reciprocal_rank"] for result in results
    ) / number_of_questions

    mean_hit_rate = sum(
        result["hit_rate"] for result in results
    ) / number_of_questions

    print("\n========== GLOBAL EVALUATION ==========")
    print(f"Number of questions: {number_of_questions}")
    print(f"Mean Recall@{K}: {mean_recall:.3f}")
    print(f"Mean Precision@{K}: {mean_precision:.3f}")
    print(f"MRR: {mean_reciprocal_rank:.3f}")
    print(f"Mean Hit Rate@{K}: {mean_hit_rate:.3f}")



if __name__ == "__main__":
    results = run_evaluation()
    calculate_global_metrics(results)
