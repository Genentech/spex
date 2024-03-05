1.
py transformation_for_file.py orig_file_csv_in transformed_file_csv_out markers
py transformation_for_file.py training.csv training_transformed.csv 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27

py transformation_for_folder.py orig_folder_in transformed_folder_out markers
py transformation_for_folder.py testing testing_transformed 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27

2.
py zscore_for_file.py transformed_file_csv_in zscore_file_csv_out markers
py zscore_for_file.py training_transformed.csv training_zscore.csv 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27

py zscore_for_folder_per_sample.py transformed_folder_in zscore_folder_out markers
py zscore_for_folder_per_sample.py testing_transformed testing_zscore_per_sample 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27

py zscore_for_folder_bulk.py transformed_folder_in zscore_folder_out markers
py zscore_for_folder_bulk.py testing_transformed testing_zscore_bulk 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27

3.
py cluster_for_file.py orig_file_csv_in transformed_or_zscore_file_csv_in clustered_file_csv_out kNN markers
py cluster_for_file.py training.csv training_zscore.csv training_clustered.csv 30 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27

py cluster_for_folder_per_sample.py orig_folder_in transformed_or_zscore_folder_in clustered_folder_out kNN markers
py cluster_for_folder_per_sample.py testing testing_zscore_per_sample testing_clustered_per_sample 30 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27

py cluster_for_folder_bulk.py orig_folder_in transformed_or_zscore_folder_in clustered_folder_out kNN markers
py cluster_for_folder_bulk.py testing testing_zscore_bulk testing_clustered_bulk 30 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27

4.
py dml.py clustered_training_file_csv_in transformed_or_zscore_file_csv_in orig_testing_folder_in transformed_or_zscore_testing_folder_in training_dml_csv_out testing_dml_folder_out n_neighbors min_dist markers
py dml.py training_clustered.csv training_zscore.csv testing testing_zscore_bulk training_dml.csv testing_dml 30 0.3 5,7,8,9,11,12,15,16,17,18,19,21,22,24,26,27

5.
py qfmatch.py left_file_csv_in right_file_csv_in match_result_file_png_out match_result_file_csv_out bin_size cluster_id_column x_columns
py qfmatch.py training_dml.csv testing_dml\KBM0201f_Slide2_17505_IPF.csv match_result.png match_result.csv 60 32 30,31