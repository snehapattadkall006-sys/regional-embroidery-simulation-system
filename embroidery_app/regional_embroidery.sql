-- Regional Embroidery Simulation System - Database Schema
-- Run this script in MySQL to set up the database

CREATE DATABASE IF NOT EXISTS regional_embroidery;
USE regional_embroidery;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Admin table
CREATE TABLE IF NOT EXISTS admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);

-- Designs table
CREATE TABLE IF NOT EXISTS designs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    state VARCHAR(100) NOT NULL,
    name VARCHAR(150) NOT NULL,
    image VARCHAR(500),
    history TEXT,
    community TEXT,
    materials TEXT,
    fabric_type VARCHAR(200),
    description TEXT,
    cultural_significance TEXT,
    traditional_usage TEXT,
    techniques TEXT
);

-- Saved designs table
CREATE TABLE IF NOT EXISTS saved_designs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    design_id INT NOT NULL,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (design_id) REFERENCES designs(id) ON DELETE CASCADE
);

-- Favorites table
CREATE TABLE IF NOT EXISTS favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    design_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (design_id) REFERENCES designs(id) ON DELETE CASCADE
);

-- Feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Design views table
CREATE TABLE IF NOT EXISTS design_views (
    id INT AUTO_INCREMENT PRIMARY KEY,
    design_name VARCHAR(150) NOT NULL,
    viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Downloads table
CREATE TABLE IF NOT EXISTS downloads (
    id INT AUTO_INCREMENT PRIMARY KEY,
    design_name VARCHAR(150) NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- -----------------------------------------------
-- SAMPLE DATA
-- -----------------------------------------------

-- Default admin (password: Admin@123)
INSERT INTO admin (email, password) VALUES
('admin@embroidery.com', 'pbkdf2:sha256:600000$admin$hashedpassword');

-- Embroidery designs
INSERT INTO designs (state, name, image, history, community, materials, fabric_type, description, cultural_significance, traditional_usage, techniques) VALUES
(
    'Karnataka',
    'Kasuti',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Kasuti_embroidery.jpg/800px-Kasuti_embroidery.jpg',
    'Kasuti is a traditional form of folk embroidery practiced in the state of Karnataka, India. Dating back over 3000 years, this ancient art form finds mention in classical Kannada literature and was historically practiced by women of the Lingayat community. The word "Kasuti" is believed to be derived from "Kai" (hand) and "suti" (cotton), literally meaning hand embroidery with cotton thread. During the reign of the Chalukyas and later the Vijayanagara Empire, Kasuti flourished as a royal craft. It was traditionally done on Ilkal sarees and pattu sarees.',
    'Lingayat community women of Karnataka, especially in districts of Dharwad, Gadag, Haveri, and Bijapur',
    'Silk thread, cotton thread, cotton fabric, needles, embroidery hoop',
    'Silk, Cotton, Ilkal Saree fabric',
    'Kasuti is a meticulous folk embroidery from Karnataka featuring geometric and floral patterns created without knots.',
    'Kasuti holds deep cultural significance as it was traditionally part of a bride''s trousseau. Each pattern tells a story from Hindu mythology including temple gopurams, palanquins (chariot), lotus flowers, and creepers. It represents the artistic heritage of Karnataka and is used in auspicious occasions.',
    'Traditionally used on Ilkal sarees, Chandrakali sarees, blouses, and ceremonial garments. Also found on household items like bedspreads and cushion covers.',
    'Four main stitches: Murgi (zigzag), Negi (running stitch), Gavanti (double running), and Menthi (cross stitch). All stitches are reversible with no knots.'
),
(
    'Gujarat',
    'Kutch Embroidery',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/5/50/Kutch_embroidery.jpg/800px-Kutch_embroidery.jpg',
    'Kutch embroidery originates from the Kutch district of Gujarat and has a rich history spanning over 1000 years. It is believed to have been brought to Gujarat by communities migrating from Sindh (now Pakistan). The embroidery is renowned for its intricate mirror work (shisha), vibrant colors, and complex geometric and floral patterns. Historically, different communities in Kutch developed their own distinct styles - the Ahirs, Meghwals, Mutvas, Rabaris, and Sodhas each have unique embroidery traditions that can be identified by their characteristic patterns and techniques.',
    'Ahir, Meghwal, Mutva, Rabari, and Sodha communities of Kutch district, Gujarat',
    'Silk thread, mirror pieces (shisha), cotton fabric, woolen thread, gold/silver thread, needles',
    'Cotton, Silk, Wool, Canvas',
    'Vibrant geometric embroidery with mirror work from the Kutch region of Gujarat, featuring bold colors and intricate stitchwork.',
    'Kutch embroidery is deeply embedded in the social and religious fabric of the communities. Each community has its distinct style used to mark life events, festivals, and social status. The work is passed down through generations as a vital cultural inheritance.',
    'Used on traditional attire like ghaghra-choli (skirt-blouse), odhani (dupatta), wall hangings (torans), bags, and decorative household items. Worn during festivals, weddings, and religious ceremonies.',
    'Interlaced buttonhole stitch, chain stitch, satin stitch combined with mirror (shisha) work. Patterns include geometric shapes, birds, animals, and floral motifs.'
),
(
    'Uttar Pradesh',
    'Chikankari',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8d/Chikan_embroidery.jpg/800px-Chikan_embroidery.jpg',
    'Chikankari is one of Lucknow''s most celebrated traditional crafts with a history of over 400 years. Legend attributes its origin to Nur Jahan, the wife of Mughal Emperor Jahangir, who introduced this delicate embroidery in the 17th century. The word "Chikan" is derived from the Persian word meaning embroidery. During the Nawabi era of Lucknow, Chikankari reached its zenith of refinement and elegance. The Nawabs of Awadh were great patrons of this art, and it became synonymous with Lucknawi tehzeeb (culture). After the decline of the Nawabs, it became a cottage industry supporting thousands of artisan families.',
    'Muslim and Hindu artisan communities (Karigar) of Lucknow, particularly in old city areas like Chowk and Aminabad',
    'White cotton thread on white muslin/cotton fabric, needles, thimble, chalk for tracing patterns',
    'Muslin, Cotton, Georgette, Chiffon, Silk',
    'Delicate white-on-white shadow embroidery from Lucknow featuring over 32 different stitch styles.',
    'Chikankari represents the refinement and sophistication of Lucknow''s Nawabi culture. Traditionally done in white thread on white fabric, it embodies understated elegance. It is a GI (Geographical Indication) tagged craft and is recognized as one of India''s most prestigious textile traditions.',
    'Traditional garments include kurtas, sarees, salwar suits, and dupattas. Popular for formal and semi-formal occasions. The Prime Minister of India has popularized Chikankari kurtas on global platforms.',
    'Over 32 distinct stitches including Taipchi (basic running stitch), Bakhiya (shadow work), Jali (net pattern), Murri (French knot), Phanda, and Khatao (applique).'
),
(
    'Punjab',
    'Phulkari',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/3/39/Phulkari_embroidery.jpg/800px-Phulkari_embroidery.jpg',
    'Phulkari, meaning "flower work," is a traditional embroidery of the Punjab region with roots stretching back to the 15th century. It finds mention in the great Punjabi epic Heer Ranjha by Waris Shah. Historically, Phulkari was created by women for personal use and was never sold commercially - it was an expression of love, labor, and artistry. Every bride in Punjab would have a collection of Phulkaris in her trousseau, many of which were made by her family and friends over years. The most elaborate form, called Bagh (garden), covers the entire base fabric with embroidery. Different regional variants include Chope, Vari-da-Bagh, and Thirma.',
    'Women of all communities in Punjab including Jat, Khatri, and Arora communities; also practiced in Haryana and parts of Rajasthan',
    'Silk floss thread (patt), coarse handspun cotton fabric (khaddar), needles',
    'Khaddar (handspun cotton), Coarse cotton',
    'Vibrant floral embroidery done on coarse cotton fabric using silk threads, creating dazzling geometric flower patterns.',
    'Phulkari is intimately connected to the cycle of life in Punjab. Made during births, weddings, and festivals, each Phulkari tells the story of Punjabi culture. The iconic orange-red Phulkari is considered auspicious and is part of every Punjabi bride''s wedding ensemble.',
    'Traditional shawls, dupattas, and head covers for women. Used during weddings, festivals like Teej and Vaisakhi, and religious ceremonies. Modern adaptations include suits, kurtas, and home furnishings.',
    'Darning stitch worked from the wrong side of the fabric, creating geometric patterns. The thread is passed through the warp threads of the fabric in horizontal rows. Motifs include flowers, birds, geometric shapes, and everyday objects.'
),
(
    'Rajasthan',
    'Gota Patti',
    'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Gota_Patti_embroidery.jpg/800px-Gota_Patti_embroidery.jpg',
    'Gota Patti is a traditional form of embroidery and applique work that originated in the royal courts of Rajasthan, particularly in Jaipur. Dating back to the 17th century Mughal era, this exquisite craft involves the application of gold and silver ribbon (gota) onto fabric to create stunning patterns. The craft was historically patronized by the royal families of Rajputana and was used to embellish royal garments, turbans (pagris), and ceremonial items. The name comes from "gota" (ribbon of gold or silver) and "patti" (strip). Jaipur remains the center of this craft and has GI tag recognition for Gota Patti work.',
    'Artisan communities of Jaipur, Ajmer, and surrounding areas in Rajasthan; traditionally practiced by the Manihar and other communities',
    'Gold and silver ribbon (gota), silk fabric, golden zari thread, sequins, beads, needles',
    'Silk, Net, Georgette, Velvet',
    'Opulent gold ribbon applique work from Rajasthan creating three-dimensional floral patterns on rich fabrics.',
    'Gota Patti is synonymous with Rajasthani royalty and celebration. Traditionally used in royal weddings and ceremonies, it symbolizes prosperity and grandeur. The craft is deeply embedded in Rajasthani bridal culture and festival celebrations, particularly during Teej and Gangaur festivals.',
    'Primarily used on bridal lehengas, sarees, blouses, turbans, and ceremonial wear. Also used on home decor items like cushion covers and wall hangings. Popular across India for wedding and festive occasions.',
    'Applique technique where gota ribbon is folded, pleated, and stitched onto fabric to create three-dimensional floral and geometric motifs. Supplemented with zardozi embroidery, sequin work, and mirror work.'
);

-- -----------------------------------------------
-- ADDITIONAL QUERIES FOR ANALYTICS (sample data)
-- -----------------------------------------------

-- Sample design views
INSERT INTO design_views (design_name, viewed_at) VALUES
('Kasuti', NOW()), ('Kutch Embroidery', NOW()), ('Chikankari', NOW()),
('Phulkari', NOW()), ('Gota Patti', NOW()), ('Kasuti', DATE_SUB(NOW(), INTERVAL 1 DAY)),
('Chikankari', DATE_SUB(NOW(), INTERVAL 2 DAY)), ('Phulkari', DATE_SUB(NOW(), INTERVAL 3 DAY));
