# RAG Evaluation Report

## 1. Objective

The objective of this evaluation is to measure the retrieval performance of the Enterprise RAG Assistant and compare two embedding models.

The evaluation focuses on the ability of the system to retrieve relevant document chunks for a given question.

## 2. Evaluation Dataset

The evaluation uses:
- 20 questions written in French.
- One six-page PDF document.
- 29 relevance annotations across the 20 questions.
- Manually identified relevant chunks for each question.

The document is a practical workshop about supervised learning with Python, including classification, preprocessing, feature selection and model optimization.

## 3. Evaluation Methodology

For each question:

1. Generate an embedding for the question.
2. Retrieve the five most relevant chunks from PostgreSQL using pgvector.
3. Compare retrieved chunk IDs with manually annotated relevant chunk IDs.
4. Calculate the evaluation metrics.

The retrieval process uses cosine distance.

The evaluation was performed with two embedding models:

- Baseline: `all-MiniLM-L6-v2`
- Selected model: `paraphrase-multilingual-MiniLM-L12-v2`

Both models produce 384-dimensional embeddings.

## 4. Evaluation Metrics

Four metrics are used:

- **Recall@5:** proportion of relevant chunks retrieved among all relevant chunks.
- **Precision@5:** proportion of relevant chunks among the five retrieved results.
- **Mean Reciprocal Rank (MRR):** evaluates the ranking position of the first relevant result.
- **Hit Rate@5:** proportion of questions for which at least one relevant chunk is retrieved in the top five results.

## 5. Results

| Metric | Baseline Model | Multilingual Model |
|---|---:|---:|
| Recall@5 | 0.675 | 0.750 |
| Precision@5 | 0.200 | 0.210 |
| MRR | 0.564 | 0.660 |
| Hit Rate@5 | 0.800 | 0.900 |

The multilingual model improves all four evaluation metrics.

The most significant improvement is observed in MRR, which increases from 0.564 to 0.660.

The Hit Rate@5 reaches 0.900, meaning that at least one relevant chunk is retrieved for 18 out of 20 questions.

## 6. Model Selection

Based on the evaluation results, `paraphrase-multilingual-MiniLM-L12-v2` was selected.

This model provides better retrieval performance on the current French evaluation dataset while preserving the existing 384-dimensional vector database structure.

The embeddings stored in PostgreSQL were regenerated using the selected model.

A new evaluation was then performed directly against PostgreSQL and confirmed the same results as the initial in-memory experiment.

## 7. Limitations

The evaluation has several limitations:

- The dataset contains only 20 questions.
- The evaluation currently uses a single PDF document.
- The relevance annotations are manually defined.
- Some exact technical terms and filenames are not consistently retrieved in the top five results.

Questions Q02 and Q11 did not retrieve a relevant chunk in the top five results.

These limitations suggest possible future improvements, such as hybrid retrieval combining semantic and lexical search.

## 8. Conclusion

The evaluation confirms that the multilingual embedding model improves retrieval performance on the current dataset.

The system achieves a Recall@5 of 0.750, an MRR of 0.660 and a Hit Rate@5 of 0.900.

These results provide a quantitative baseline for future improvements to the Enterprise RAG Assistant.
