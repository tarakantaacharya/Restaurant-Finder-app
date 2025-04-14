-- Create the users table for authentication
CREATE TABLE IF NOT EXISTS `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL UNIQUE,
  `password_hash` varchar(255) NOT NULL,
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert a default admin user (password: admin123)
INSERT INTO `users` (`name`, `email`, `password_hash`) 
VALUES ('Admin User', 'admin@example.com', '$2b$12$tGpRxMfWD5e8x1n.QHL0B.jvEYXxQsB3RkzW9oVLBW0Cq9PHoJzXO');

-- Create the zomato_new table
CREATE TABLE IF NOT EXISTS `zomato_new` (
  `Restaurant_ID` int NOT NULL,
  `Restaurant_Name` varchar(255) DEFAULT NULL,
  `Country_Code` int DEFAULT NULL,
  `City` varchar(255) DEFAULT NULL,
  `Address` text,
  `Locality` varchar(255) DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  `Cuisine` varchar(255) DEFAULT NULL,
  `Avg_Cost_for_Two` int DEFAULT NULL,
  `Currency` varchar(10) DEFAULT NULL,
  `Has_Table_booking` varchar(5) DEFAULT NULL,
  `Has_Online_delivery` varchar(5) DEFAULT NULL,
  `Is_delivering_now` varchar(5) DEFAULT NULL,
  `Switch_to_order_menu` varchar(5) DEFAULT NULL,
  `Price_Range` int DEFAULT NULL,
  `Rating` float DEFAULT NULL,
  `Rating_Color` varchar(20) DEFAULT NULL,
  `Rating_Text` varchar(20) DEFAULT NULL,
  `Total_Votes` int DEFAULT NULL,
  `City_ID` int DEFAULT NULL,
  `featured_image` text,
  `photos_url` text,
  `menu_url` text,
  `events_url` text,
  `Restaurant_URL` text,
  `Location_Zipcode` varchar(20) DEFAULT NULL,
  `Country` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Restaurant_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create the restaurants table for nearby restaurants
CREATE TABLE IF NOT EXISTS `restaurants` (
  `Restaurant_ID` varchar(255) NOT NULL,
  `Restaurant_Name` varchar(255) DEFAULT NULL,
  `City` varchar(255) DEFAULT NULL,
  `Address` text,
  `Locality` varchar(255) DEFAULT NULL,
  `Longitude` float DEFAULT NULL,
  `Latitude` float DEFAULT NULL,
  `Cuisine` varchar(255) DEFAULT NULL,
  `Avg_Cost_for_Two` int DEFAULT NULL,
  `Currency` varchar(10) DEFAULT NULL,
  `Has_Table_booking` varchar(5) DEFAULT NULL,
  `Has_Online_delivery` varchar(5) DEFAULT NULL,
  `Is_delivering_now` varchar(5) DEFAULT NULL,
  `Switch_to_order_menu` varchar(5) DEFAULT NULL,
  `Price_Range` int DEFAULT NULL,
  `Rating` float DEFAULT NULL,
  `Rating_Color` varchar(20) DEFAULT NULL,
  `Rating_Text` varchar(20) DEFAULT NULL,
  `Total_Votes` int DEFAULT NULL,
  `City_ID` int DEFAULT NULL,
  `featured_image` text,
  `photos_url` text,
  `menu_url` text,
  `events_url` text,
  `Restaurant_URL` text,
  `Location_Zipcode` varchar(20) DEFAULT NULL,
  `Country` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`Restaurant_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert sample data (optional)
INSERT INTO `zomato_new` (`Restaurant_ID`, `Restaurant_Name`, `Country_Code`, `City`, `Address`, `Locality`, `Longitude`, `Latitude`, `Cuisine`, `Avg_Cost_for_Two`, `Currency`, `Has_Table_booking`, `Has_Online_delivery`, `Is_delivering_now`, `Switch_to_order_menu`, `Price_Range`, `Rating`, `Rating_Color`, `Rating_Text`, `Total_Votes`, `City_ID`, `featured_image`, `photos_url`, `menu_url`, `events_url`, `Restaurant_URL`, `Location_Zipcode`, `Country`)
VALUES
(1, 'Sample Restaurant 1', 1, 'New York', '123 Main St', 'Downtown', -73.9857, 40.7484, 'American, Italian', 50, 'USD', 'Yes', 'Yes', 'Yes', 'No', 3, 4.5, 'Green', 'Excellent', 1000, 1, 'https://example.com/image1.jpg', 'https://example.com/photos1', 'https://example.com/menu1', 'https://example.com/events1', 'https://example.com/restaurant1', '10001', 'USA'),
(2, 'Sample Restaurant 2', 1, 'New York', '456 Broadway', 'Midtown', -73.9877, 40.7587, 'Chinese, Thai', 40, 'USD', 'No', 'Yes', 'Yes', 'No', 2, 4.0, 'Green', 'Very Good', 800, 1, 'https://example.com/image2.jpg', 'https://example.com/photos2', 'https://example.com/menu2', 'https://example.com/events2', 'https://example.com/restaurant2', '10002', 'USA'),
(3, 'Sample Restaurant 3', 1, 'Los Angeles', '789 Hollywood Blvd', 'Hollywood', -118.3267, 34.1016, 'Mexican, Spanish', 60, 'USD', 'Yes', 'No', 'No', 'No', 4, 4.8, 'Dark Green', 'Excellent', 1200, 2, 'https://example.com/image3.jpg', 'https://example.com/photos3', 'https://example.com/menu3', 'https://example.com/events3', 'https://example.com/restaurant3', '90028', 'USA');