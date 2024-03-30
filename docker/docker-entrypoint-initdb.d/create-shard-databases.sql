CREATE DATABASE `tend_attend_shard0`;
CREATE DATABASE `tend_attend_shard1`;
GRANT ALL PRIVILEGES ON `tend_attend_shard0`.* TO `user`@`%`;
GRANT ALL PRIVILEGES ON `tend_attend_shard1`.* TO `user`@`%`;
