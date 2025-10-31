from sklearn.metrics import f1_score, accuracy_score


def evaluate_classification(preds, labels):
    acc = accuracy_score(labels, preds)
    f1 = f1_score(labels, preds, average="macro")
    return {"accuracy": acc, "f1": f1}
