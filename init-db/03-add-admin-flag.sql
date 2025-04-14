-- Add is_admin column to users table
ALTER TABLE `users` ADD COLUMN `is_admin` BOOLEAN NOT NULL DEFAULT FALSE;

-- Set the default admin user as admin
UPDATE `users` SET `is_admin` = TRUE WHERE `email` = 'admin@example.com';

-- Create a table for site settings
CREATE TABLE IF NOT EXISTS `site_settings` (
  `id` int NOT NULL AUTO_INCREMENT,
  `setting_key` varchar(255) NOT NULL UNIQUE,
  `setting_value` text NOT NULL,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert default color theme setting
INSERT INTO `site_settings` (`setting_key`, `setting_value`) 
VALUES ('color_theme', 'orange');