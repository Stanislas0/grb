## Attack
# full
python attack_pipeline.py \
--n_epoch 2000 \
--lr 0.01 \
--dataset grb-reddit \
--dataset_mode full \
--feat_norm arctan \
--data_dir ../data/grb-reddit/ \
--config_dir ./grb-reddit/ \
--model_dir ../saved_models/grb-reddit-arctan-ind-sur/ \
--model gcn \
--save_dir ../results/grb-reddit-arctan-ind/ \
--n_attack 10 \
--n_inject 600 \
--n_edge_max 200 \
--feat_lim_min -1 \
--feat_lim_max 1 \
--gpu 1

# easy
python attack_pipeline.py \
--n_epoch 2000 \
--lr 0.01 \
--dataset grb-reddit \
--dataset_mode easy \
--feat_norm arctan \
--data_dir ../data/grb-reddit/ \
--config_dir ./grb-reddit/ \
--model_dir ../saved_models/grb-reddit-arctan-ind-sur/ \
--model gcn \
--save_dir ../results/grb-reddit-arctan-ind/ \
--n_attack 10 \
--n_inject 200 \
--n_edge_max 200 \
--feat_lim_min -1 \
--feat_lim_max 1 \
--gpu 1

# medium
python attack_pipeline.py \
--n_epoch 2000 \
--lr 0.01 \
--dataset grb-reddit \
--dataset_mode medium \
--feat_norm arctan \
--data_dir ../data/grb-reddit/ \
--config_dir ./grb-reddit/ \
--model_dir ../saved_models/grb-reddit-arctan-ind-sur/ \
--model gcn \
--save_dir ../results/grb-reddit-arctan-ind/ \
--n_attack 10 \
--n_inject 200 \
--n_edge_max 200 \
--feat_lim_min -1 \
--feat_lim_max 1 \
--gpu 1

# hard
python attack_pipeline.py \
--n_epoch 2000 \
--lr 0.01 \
--dataset grb-reddit \
--dataset_mode hard \
--feat_norm arctan \
--data_dir ../data/grb-reddit/ \
--config_dir ./grb-reddit/ \
--model_dir ../saved_models/grb-reddit-arctan-ind-sur/ \
--model gcn \
--save_dir ../results/grb-reddit-arctan-ind/ \
--n_attack 10 \
--n_inject 200 \
--n_edge_max 200 \
--feat_lim_min -1 \
--feat_lim_max 1 \
--gpu 0