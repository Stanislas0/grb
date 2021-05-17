import os
import time
import scipy
import torch
import torch.nn.functional as F

import grb.utils as utils
from grb.utils import evaluator


class Trainer(object):
    def __init__(self, dataset, optimizer, loss, adj_norm_func=None, lr_scheduler=None, early_stop=None, device='cpu'):

        # Load dataset
        self.adj = dataset.adj
        self.features = dataset.features
        self.labels = dataset.labels
        self.train_mask = dataset.train_mask
        self.val_mask = dataset.val_mask
        self.test_mask = dataset.test_mask
        self.num_classes = dataset.num_classes

        # Convert to tensor
        self.device = device
        if adj_norm_func is not None:
            self.prepare(adj_norm_func=adj_norm_func)
        else:
            self.prepare()

        # Settings
        self.optimizer = optimizer
        self.loss = loss

        # Learning rate scheduling
        if lr_scheduler:
            self.lr_scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(
                self.optimizer,
                mode='min',
                patience=100,
                factor=0.75,
                min_lr=0.0,
                verbose=True)
        else:
            self.lr_scheduler = lr_scheduler

        # Early stop
        if early_stop:
            self.early_stop = EarlyStop()
        else:
            self.early_stop = early_stop

    def prepare(self, adj_norm_func=None):
        if type(self.adj) != scipy.sparse.coo.coo_matrix:
            self.adj = self.adj.tocoo()
        if adj_norm_func is not None:
            self.adj = adj_norm_func(self.adj)
        if type(self.adj) is tuple:
            self.adj = [utils.adj_to_tensor(adj).to(self.device) for adj in self.adj]
        else:
            self.adj = utils.adj_to_tensor(self.adj).to(self.device)
        self.features = torch.FloatTensor(self.features).to(self.device)
        self.labels = torch.LongTensor(self.labels).to(self.device)

    def train(self, model, n_epoch, save_dir=None, save_name=None,
              eval_every=10, save_after=0, dropout=0, verbose=True):
        model.to(self.device)
        model.train()

        if save_dir is None:
            cur_time = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())
            save_dir = "./tmp_{}".format(cur_time)
        else:
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)

        if save_name is None:
            save_name = "checkpoint.pt"
        else:
            if save_name.split(".")[-1] != "pt":
                save_name = save_name + ".pt"

        train_acc_list = []
        val_acc_list = []
        best_val_acc = 0.0
        for epoch in range(n_epoch):
            logits = model(self.features, self.adj, dropout)
            logp = F.log_softmax(logits, 1)
            train_loss = F.nll_loss(logp[self.train_mask], self.labels[self.train_mask])
            val_loss = F.nll_loss(logp[self.val_mask], self.labels[self.val_mask])

            self.optimizer.zero_grad()
            train_loss.backward()
            self.optimizer.step()

            if self.lr_scheduler:
                self.lr_scheduler.step(val_loss)
            if self.early_stop:
                self.early_stop(val_loss)
                if self.early_stop.stop:
                    print("Training early stopped.")
                    utils.save_model(model, save_dir, "checkpoint_epoch_{}_early_stopped.pt".format(epoch))

                    # return train_acc_list, val_acc_list

            if epoch % eval_every == 0:
                train_acc = evaluator.eval_acc(logp, self.labels, self.train_mask)
                val_acc = evaluator.eval_acc(logp, self.labels, self.val_mask)
                train_acc_list.append(train_acc)
                val_acc_list.append(val_acc)
                if val_acc > best_val_acc:
                    best_val_acc = val_acc
                    if epoch > save_after:
                        print("Best validation accuracy: {:.4f}".format(best_val_acc))
                        utils.save_model(model, save_dir, save_name)
                if verbose:
                    print(
                        'Epoch {:05d} | Train Loss {:.4f} | Train Acc {:.4f} | Val Loss {:.4f} | Val Acc {:.4f}'.format(
                            epoch, train_loss, train_acc, val_loss, val_acc))

        utils.save_model(model, save_dir, "checkpoint_final.pt")

    def inference(self, model):
        model.to(self.device)
        model.eval()
        logits = model(self.features, self.adj, dropout=0)
        logp = F.softmax(logits, 1)
        test_acc = evaluator.eval_acc(logp, self.labels, self.test_mask)

        return logits, test_acc


class EarlyStop(object):
    def __init__(self, patience=100, epsilon=1e-5):
        self.patience = patience
        self.epsilon = epsilon
        self.min_loss = None
        self.stop = False
        self.count = 0

    def __call__(self, val_loss):
        if self.min_loss is None:
            self.min_loss = val_loss
        elif self.min_loss - val_loss > self.epsilon:
            self.count = 0
            self.min_loss = val_loss
        elif self.min_loss - val_loss < self.epsilon:
            self.count += 1
            if self.count > self.patience:
                self.stop = True
