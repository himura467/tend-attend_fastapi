CREATE DATABASE `test_ta_shard0`;
CREATE DATABASE `test_ta_shard1`;
GRANT ALL PRIVILEGES ON `test_ta_shard0`.* TO `user`@`%`;
GRANT ALL PRIVILEGES ON `test_ta_shard1`.* TO `user`@`%`;
