-- 查询邮箱是否与头像散列值对应
SELECT
    customer_email AS 邮箱,
    customer_name AS 用户名,
    role_name AS 身份,
    head_portrait AS 头像文件,
    MD5(customer_email) = SUBSTR(head_portrait, 1, INSTR(head_portrait, '.') - 1) AS 符合映射
FROM customers AS c
INNER JOIN roles AS r
ON c.role_id = r.role_id;

-- 查询关注关系
SELECT f.customer_name 粉丝, a.customer_name 作者
FROM follows
INNER JOIN customers f
ON follows.fans_id = f.customer_id
INNER JOIN customers a
ON follows.author_id = a.customer_id;

-- 建立articles表
CREATE TABLE IF NOT EXISTS articles(
    article_id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(128) NOT NULL,
    content TEXT NOT NULL,
    content_html TEXT NOT NULL,
    publish_time DATETIME NOT NULL,
    author_id INT NOT NULL,
    CONSTRAINT fk_articles_customers FOREIGN KEY(author_id) REFERENCES customers(customer_id)
);

-- 查询用户关注的作者发布的文章，按照发布时间排序，最新在前
SELECT
    author.customer_name AS 作者,
    author.head_portrait AS 头像,
    a.publish_time AS 发布时间,
    a.article_id AS 文章ID,
    a.title AS 文章标题
FROM follows AS f
INNER JOIN customers AS fans
ON f.fans_id = fans.customer_id
INNER JOIN customers AS author
ON f.author_id = author.customer_id
INNER JOIN articles AS a
ON author.customer_id = a.author_id
WHERE fans.customer_name = 'FlaskyAdmin'
ORDER BY a.publish_time DESC;

-- 建立comments表
CREATE TABLE IF NOT EXISTS comments(
    comment_id INT PRIMARY KEY AUTO_INCREMENT,
    content TEXT NOT NULL,
    content_html TEXT NOT NULL,
    comment_time DATETIME NOT NULL,
    disabled TINYINT(1) NOT NULL DEFAULT 0,
    author_id INT NOT NULL,
    article_id INT NOT NULL,

    CONSTRAINT fk_comments_customers FOREIGN KEY(author_id) REFERENCES customers(customer_id),
    CONSTRAINT fk_comments_articles FOREIGN KEY(article_id) REFERENCES articles(article_id)
);

-- 多对多关系的练习
-- 建表
CREATE TABLE IF NOT EXISTS students(
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    student_name VARCHAR(255) NOT NULL
);
INSERT INTO students(student_name)
VALUES('谢基悦'), ('刘华烨'), ('何子兴'), ('潘香芩'), ('方芳');

CREATE TABLE IF NOT EXISTS classes(
    class_id INT PRIMARY KEY AUTO_INCREMENT,
    class_name VARCHAR(255) NOT NULL UNIQUE
);
INSERT INTO classes(class_name)
VALUES('数学分析'), ('高等数学'), ('线性代数'), ('高等代数'), ('近世代数'), ('微分几何');

CREATE TABLE IF NOT EXISTS relationship(
    student_id INT NOT NULL,
    class_id INT NOT NULL,
    CONSTRAINT fk_relationship_students FOREIGN KEY(student_id) REFERENCES students(student_id),
    CONSTRAINT fk_relationship_classes FOREIGN KEY(class_id) REFERENCES classes(class_id)
);
INSERT INTO relationship
SET student_id=(SELECT student_id FROM students WHERE student_name='谢基悦'),
class_id=(SELECT class_id FROM classes WHERE class_name='数学分析');
INSERT INTO relationship
SET student_id=(SELECT student_id FROM students WHERE student_name='谢基悦'),
class_id=(SELECT class_id FROM classes WHERE class_name='高等代数');
INSERT INTO relationship
SET student_id=(SELECT student_id FROM students WHERE student_name='刘华烨'),
class_id=(SELECT class_id FROM classes WHERE class_name='数学分析');
INSERT INTO relationship
SET student_id=(SELECT student_id FROM students WHERE student_name='刘华烨'),
class_id=(SELECT class_id FROM classes WHERE class_name='高等代数');
INSERT INTO relationship
SET student_id=(SELECT student_id FROM students WHERE student_name='何子兴'),
class_id=(SELECT class_id FROM classes WHERE class_name='数学分析');
INSERT INTO relationship
SET student_id=(SELECT student_id FROM students WHERE student_name='何子兴'),
class_id=(SELECT class_id FROM classes WHERE class_name='高等代数');
INSERT INTO relationship
SET student_id=(SELECT student_id FROM students WHERE student_name='潘香芩'),
class_id=(SELECT class_id FROM classes WHERE class_name='高等数学');
INSERT INTO relationship
SET student_id=(SELECT student_id FROM students WHERE student_name='潘香芩'),
class_id=(SELECT class_id FROM classes WHERE class_name='线性代数');
INSERT INTO relationship
SET student_id=(SELECT student_id FROM students WHERE student_name='方芳'),
class_id=(SELECT class_id FROM classes WHERE class_name='高等数学');
INSERT INTO relationship
SET student_id=(SELECT student_id FROM students WHERE student_name='方芳'),
class_id=(SELECT class_id FROM classes WHERE class_name='线性代数');

-- 查询
SELECT c.class_name 谢基悦的课程
FROM students s
INNER JOIN relationship r
ON s.student_id=r.student_id
INNER JOIN classes c
ON r.class_id=c.class_id
WHERE s.student_name='谢基悦';

SELECT s.student_name 数学分析课的同学
FROM students s
INNER JOIN relationship r
ON s.student_id=r.student_id
INNER JOIN classes c
ON r.class_id=c.class_id
WHERE c.class_name='数学分析';

SELECT class_name 谢基悦的课程
FROM classes
WHERE class_id IN (
    SELECT class_id
    FROM relationship
    WHERE student_id = (
        SELECT student_id
        FROM students
        WHERE student_name = '谢基悦'
    )
);

SELECT student_name 数学分析课的同学
FROM students
WHERE student_id IN (
    SELECT student_id
    FROM relationship
    WHERE class_id = (
        SELECT class_id
        FROM classes
        WHERE class_name = '数学分析'
    )
);

-- 建立关注者与被关注者的关系，在数据库中表现为customers的自引用关系
CREATE TABLE IF NOT EXISTS follows(
    fans_id INT NOT NULL,
    author_id INT NOT NULL,
    follow_time DATETIME NOT NULL,
    FOREIGN KEY(fans_id) REFERENCES customers(customer_id),
    FOREIGN KEY(author_id) REFERENCES customers(customer_id)
);
