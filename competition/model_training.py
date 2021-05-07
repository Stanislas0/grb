import argparse
import os
import pickle
import sys

import numpy as np
import torch
import torch.nn.functional as F

sys.path.append('..')

from grb.dataset.dataset import CustomDataset
from grb.model.trainer import Trainer
from grb.utils import normalize

sys.path.append('..')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Training GNN models')
    parser.add_argument("--gpu", type=int, default=0, help="gpu")
    parser.add_argument("--n_epoch", type=int, default=10, help="Training epoch.")
    parser.add_argument("--lr", type=float, default=0.01, help="Learning rate.")
    parser.add_argument("--eval_every", type=int, default=100)
    parser.add_argument("--save_after", type=int, default=2000)
    parser.add_argument("--data_dir", type=str, default="/data/qinkai/aminer_revised/")
    parser.add_argument("--model_dir", type=str, default="./saved_models/")
    parser.add_argument("--model_name", type=str, default="gcn_ln")
    parser.add_argument("--model_suffix", type=str, default="aminer")
    parser.add_argument("--early_stop", action='store_true')
    parser.add_argument("--lr_scheduler", action='store_true')
    parser.add_argument("--dropout", type=float, default=0.5)
    parser.add_argument("--seed", type=int, default=0)

    args = parser.parse_args()

    if args.gpu >= 0:
        device = "cuda:{}".format(args.gpu)
    else:
        device = "cpu"

    data_dir = args.data_dir
    with open(os.path.join(data_dir, "adj.pkl"), 'rb') as f:
        adj = pickle.load(f)
    labels = np.load(os.path.join(data_dir, "labels_train.npy"))
    features = np.load(os.path.join(data_dir, "features.npy"))
    labels_test = np.load(os.path.join(data_dir, "labels_test.npy"))
    labels = np.concatenate([labels, labels_test], axis=0)

    n_node = features.shape[0]
    n_val = 50000  # user-defined val size
    n_test = 50000
    train_mask = torch.zeros(n_node, dtype=bool)
    train_mask[range(n_node - n_val - n_test)] = True
    val_mask = torch.zeros(n_node, dtype=bool)
    val_mask[range(n_node - n_val - n_test, n_node - n_test)] = True
    test_mask = torch.zeros(n_node, dtype=bool)
    test_mask[range(n_node - n_test, n_node)] = True

    dataset = CustomDataset(adj=adj,
                            features=features,
                            labels=labels,
                            train_mask=train_mask,
                            val_mask=val_mask,
                            test_mask=test_mask,
                            name='Aminer')
    adj = dataset.adj
    adj_tensor = dataset.adj_tensor
    features = dataset.features
    labels = dataset.labels
    num_features = dataset.num_features
    num_classes = dataset.num_classes

    model_name = args.model_name
    if model_name in "gcn_ln":
        from grb.model.gcn import GCN

        model = GCN(in_features=num_features,
                    out_features=num_classes,
                    hidden_features=[256, 128, 64],
                    layer_norm=True,
                    activation=F.relu)
        adj_norm_func = normalize.GCNAdjNorm
    elif model_name in "graphsage":
        from grb.model.graphsage import GraphSAGE

        model = GraphSAGE(in_features=num_features, out_features=num_classes,
                          hidden_features=[128, 128, 128], activation=F.relu)
        adj_norm_func = normalize.SAGEAdjNorm
    elif model_name in "sgcn":
        from grb.model.sgcn import SGCN

        model = SGCN(in_features=num_features, out_features=num_classes, hidden_features=[128, 128, 128],
                     activation=F.relu)
        adj_norm_func = normalize.GCNAdjNorm
    elif model_name in "robustgcn":
        from grb.model.robustgcn import RobustGCN

        model = RobustGCN(in_features=num_features, out_features=num_classes,
                          hidden_features=[128, 128, 128])
        adj_norm_func = normalize.RobustGCNAdjNorm
    elif model_name in "tagcn":
        from grb.model.tagcn import TAGCN

        model = TAGCN(in_features=num_features, out_features=num_classes, hidden_features=[128, 128, 128],
                      k=2, activation=F.leaky_relu)
        adj_norm_func = normalize.GCNAdjNorm
    elif model_name in "appnp":
        from grb.model.appnp import APPNP

        model = APPNP(in_features=num_features, out_features=num_classes, hidden_features=128,
                      alpha=0.01, k=10)
        adj_norm_func = normalize.GCNAdjNorm
    elif model_name in "gin":
        from grb.model.gin import GIN

        model = GIN(in_features=num_features, out_features=num_classes, hidden_features=[128, 128, 128],
                    activation=F.relu)
        adj_norm_func = normalize.GCNAdjNorm

    adam = torch.optim.Adam(model.parameters(), lr=args.lr)
    trainer = Trainer(dataset=dataset,
                      optimizer=adam,
                      loss=F.nll_loss,
                      adj_norm_func=adj_norm_func,
                      lr_scheduler=args.lr_scheduler,
                      early_stop=args.early_stop,
                      device=device)

    trainer.train(model=model,
                  n_epoch=args.n_epoch,
                  save_dir=os.path.join(args.model_dir, model_name + "_" + args.model_suffix),
                  eval_every=args.eval_every,
                  save_after=args.save_after,
                  dropout=args.dropout,
                  verbose=True)

    logits, test_acc = trainer.inference(model)
    print("Test ACC: {:.4f}".format(test_acc))
