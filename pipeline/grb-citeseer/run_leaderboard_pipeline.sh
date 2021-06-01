python leaderboard_pipeline.py \
--dataset grb-citeseer \
--feat_norm arctan \
--data_dir ../data/grb-citeseer/ \
--config_dir ./grb-citeseer/ \
--model_dir ../saved_models/grb-citeseer-arctan-ind/ \
--model_file 0/checkpoint.pt \
--attack_dir ../results/grb-citeseer-arctan-ind \
--attack_adj_name 0/adj.pkl \
--attack_feat_name 0/features.npy \
--weight_type polynomial \
--save_dir ./exp_results_0531/grb-citeseer/ \
--gpu 0 \
--model gcn gat graphsage gin appnp tagcn robustgcn sgcn
