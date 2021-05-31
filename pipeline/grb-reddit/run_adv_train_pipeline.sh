python adv_train_pipeline.py \
--n_epoch 12000 \
--dataset grb-reddit \
--feat_norm arctan \
--data_dir ../data/grb-reddit \
--model_dir ../saved_models/grb-reddit-arctan-ind-adv-fgsm-10/ \
--config_dir ./grb-reddit/ \
--dropout 0.5 \
--eval_every 1 \
--save_after 0 \
--early_stop \
--n_train 1 \
--train_mode inductive \
--attack_adv fgsm \
--attack_epoch 10 \
--attack_lr 0.1 \
--n_attack 1 \
--n_inject 500 \
--n_edge_max 200 \
--gpu 0