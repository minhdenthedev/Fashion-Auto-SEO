from pycocoevalcap.cider.cider import Cider

def cider_score(ground_truth, generated):
    cider_score, _ = Cider().compute_score({i: [gt] for i, gt in enumerate(ground_truth)},
                                          {i: [pred] for i, pred in enumerate(generated)})
    return cider_score