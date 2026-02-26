DELIMITER $$
DROP PROCEDURE IF EXISTS checkconflict $$
CREATE PROCEDURE checkconflict(
IN p_person_id INT,
IN p_subjid INT,
IN p_is_teacher INT,
OUT p_conflict_message VARCHAR(500)
)
BEGIN
DECLARE v_new_schedule VARCHAR(100);
DECLARE v_existing_schedule VARCHAR(100);
DECLARE v_existing_teacher_id INT DEFAULT NULL;
DECLARE v_new_days VARCHAR(10);
DECLARE v_new_timepart VARCHAR(20);
DECLARE v_new_start_str VARCHAR(10);
DECLARE v_new_end_str VARCHAR(10);
DECLARE v_new_start TIME;
DECLARE v_new_end TIME;

DECLARE v_existing_days VARCHAR(10);
DECLARE v_existing_timepart VARCHAR(20);
DECLARE v_existing_start_str VARCHAR(10);
DECLARE v_existing_end_str VARCHAR(10);
DECLARE v_existing_start TIME;
DECLARE v_existing_end TIME;

DECLARE v_pos_space INT;
DECLARE v_pos_dash INT;

DECLARE v_done INT DEFAULT 0;

DECLARE CONTINUE HANDLER FOR NOT FOUND SET v_done = 1;

SELECT subjsched INTO v_new_schedule
FROM subjects
WHERE subjid = p_subjid;

IF v_new_schedule IS NULL OR v_new_schedule = '' THEN
    SET p_conflict_message = 'Subject not found';
ELSE
    SET v_pos_space = LOCATE(' ', v_new_schedule);
    IF v_pos_space = 0 THEN
        SET p_conflict_message = 'ERROR: Invalid schedule format for new subject';
    ELSE
        SET v_new_days = LEFT(v_new_schedule, v_pos_space - 1);
        SET v_new_timepart = SUBSTRING(v_new_schedule, v_pos_space + 1);
        
        SET v_pos_dash = LOCATE('-', v_new_timepart);
        IF v_pos_dash = 0 THEN
            SET p_conflict_message = 'ERROR: Invalid time format for new subject';
        ELSE
            SET v_new_start_str = LEFT(v_new_timepart, v_pos_dash - 1);
            SET v_new_end_str = SUBSTRING(v_new_timepart, v_pos_dash + 1);
            
            SET v_new_start = STR_TO_DATE(v_new_start_str, '%H:%i');
            SET v_new_end = STR_TO_DATE(v_new_end_str, '%H:%i');
            
            SET p_conflict_message = 'No conflict';
            
            
            IF p_is_teacher = 1 THEN
                
                SELECT tid INTO v_existing_teacher_id
                FROM assign
                WHERE subjid = p_subjid
                LIMIT 1;
                
                IF v_existing_teacher_id IS NOT NULL THEN
                    SET p_conflict_message = 'Subject already assigned to another teacher';
                ELSE
                    
                    BEGIN
                        DECLARE v_cursor_teacher CURSOR FOR
                            SELECT s.subjsched 
                            FROM assign a
                            INNER JOIN subjects s ON a.subjid = s.subjid
                            WHERE a.tid = p_person_id;
                        
                        SET v_done = 0;
                        OPEN v_cursor_teacher;
                        read_loop: LOOP
                            FETCH v_cursor_teacher INTO v_existing_schedule;
                            IF v_done = 1 THEN LEAVE read_loop; END IF;
                            
                            SET v_done = 0;
                            
                            
                            SET v_pos_space = LOCATE(' ', v_existing_schedule);
                            IF v_pos_space = 0 THEN
                                SET p_conflict_message = 'ERROR: Invalid existing schedule format';
                                LEAVE read_loop;
                            END IF;
                            
                            SET v_existing_days = LEFT(v_existing_schedule, v_pos_space - 1);
                            SET v_existing_timepart = SUBSTRING(v_existing_schedule, v_pos_space + 1);
                            
                            SET v_pos_dash = LOCATE('-', v_existing_timepart);
                            IF v_pos_dash = 0 THEN
                                SET p_conflict_message = 'ERROR: Invalid existing time format';
                                LEAVE read_loop;
                            END IF;
                            
                            SET v_existing_start_str = LEFT(v_existing_timepart, v_pos_dash - 1);
                            SET v_existing_end_str = SUBSTRING(v_existing_timepart, v_pos_dash + 1);
                            
                            SET v_existing_start = STR_TO_DATE(v_existing_start_str, '%H:%i');
                            SET v_existing_end = STR_TO_DATE(v_existing_end_str, '%H:%i');
                            
                            
                            IF v_new_days = v_existing_days 
                               AND NOT (v_new_end  <= v_existing_start OR v_existing_end  <= v_new_start) THEN
                                SET p_conflict_message = CONCAT('Conflict with ', v_existing_schedule);
                                LEAVE read_loop;
                            END IF;
                        END LOOP;
                        CLOSE v_cursor_teacher;
                    END;
                END IF;
            ELSE
                 
            BEGIN
                DECLARE v_cursor_student CURSOR FOR
                    SELECT s.subjsched
                    FROM enroll e
                    INNER JOIN subjects s ON e.subjid = s.subjid
                    WHERE e.studid = p_person_id;
                
                OPEN v_cursor_student;
                read_loop: LOOP 
                    FETCH v_cursor_student INTO v_existing_schedule;
                    IF v_done = 1 THEN LEAVE read_loop; END IF;
                    
                    SET v_done = 0;
                    
                   
                    SET v_pos_space = LOCATE(' ', v_existing_schedule);
                    IF v_pos_space = 0 THEN
                        SET p_conflict_message = 'ERROR: Invalid existing schedule format';
                        LEAVE read_loop;
                    END IF;
                    
                    SET v_existing_days = LEFT(v_existing_schedule, v_pos_space - 1);
                    SET v_existing_timepart = SUBSTRING(v_existing_schedule, v_pos_space + 1);
                    
                    SET v_pos_dash = LOCATE('-', v_existing_timepart);
                    IF v_pos_dash = 0 THEN
                        SET p_conflict_message = 'ERROR: Invalid existing time format';
                        LEAVE read_loop;
                    END IF;
                    
                    SET v_existing_start_str = LEFT(v_existing_timepart, v_pos_dash - 1);
                    SET v_existing_end_str = SUBSTRING(v_existing_timepart, v_pos_dash + 1);
                    
                    SET v_existing_start = STR_TO_DATE(v_existing_start_str, '%H:%i');
                    SET v_existing_end = STR_TO_DATE(v_existing_end_str, '%H:%i');
                    
                    
                    IF v_new_days = v_existing_days 
                       AND NOT (v_new_end  <= v_existing_start OR v_existing_end  <= v_new_start) THEN
                        SET p_conflict_message = CONCAT('Conflict with ', v_existing_schedule);
                        LEAVE read_loop;
                    END IF;
                END LOOP;
                CLOSE v_cursor_student;
            END;
            END IF;
        END IF;
    END IF;
END IF;
END $$
DELIMITER ;

DELIMITER $$
DROP PROCEDURE IF EXISTS userlogin $$
CREATE PROCEDURE userlogin(
    IN p_username VARCHAR(255),
    IN p_password VARCHAR(255),
    OUT p_login_success INT,
    OUT p_message VARCHAR(255)
)
BEGIN
   
    IF p_username = 'root' AND p_password = 'root' THEN
        SET p_login_success = 1;
        SET p_message = 'Login successful';
    ELSE
        SET p_login_success = 0;
        SET p_message = 'Invalid username or password';
    END IF;
END $$
DELIMITER ;


DELIMITER $$
DROP PROCEDURE IF EXISTS grant_user_privileges $$
CREATE PROCEDURE grant_user_privileges(
    IN p_username VARCHAR(255),
    IN p_host VARCHAR(255),
    IN p_db_name VARCHAR(255),
    OUT p_result VARCHAR(255)
)
BEGIN
    DECLARE v_count INT;
    
   
    SELECT COUNT(*) INTO v_count 
    FROM information_schema.SCHEMA_PRIVILEGES 
    WHERE GRANTEE = CONCAT("'", p_username, "'@'", p_host, "'")
    AND TABLE_SCHEMA = p_db_name;
    
    IF v_count = 0 THEN
        
        SET @grant_sql = CONCAT('GRANT ALL PRIVILEGES ON ', p_db_name, '.* TO ''', p_username, '''@''', p_host, '''');
        PREPARE stmt FROM @grant_sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        
        SET p_result = 'Privileges granted successfully';
    ELSE
        SET p_result = 'Privileges already exist';
    END IF;
END $$
DELIMITER ;