python leaderboard_pipeline.py \
--dataset grb-cora \
--feat_norm arctan \
--data_dir ../data/grb-cora/ \
--config_dir ./grb-cora/ \
--model gcn gat \
--model_dir ../saved_models/grb-cora-arctan-ind/ \
--model_file 0/checkpoint.pt \
--attack_dir ../results/grb-cora-arctan-ind \
--attack_adj_name 0/adj.pkl \
--attack_feat_name 0/features.npy \
--weight_type polynomial \
--save_dir ../exp_results_0531/grb-cora/ \
--gpu 0

python leaderboard_pipeline.py \
--dataset grb-cora \
--feat_norm arctan \
--data_dir ../data/grb-cora/ \
--config_dir ./grb-cora/ \
--model gcn gat graphsage gin appnp tagcn robustgcn sgcn \
--model_dir ../saved_models/grb-cora-arctan-ind/ \
--model_file 0/checkpoint.pt \
--attack_dir ../results/grb-cora-arctan-ind \
--attack_adj_name 0/adj.pkl \
--attack_feat_name 0/features.npy \
--weight_type polynomial \
--save_dir ../exp_results_0531/grb-cora/ \
--gpu 0
