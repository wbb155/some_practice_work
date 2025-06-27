USE Student_Information;
CREATE TABLE Student(
	studentName    varchar(20)  NOT NULL,
	studentNo  char(10)     NOT NULL, 
	height     float        NOT NULL,
	CONSTRAINT studentPK PRIMARY KEY (studentNo)
)
