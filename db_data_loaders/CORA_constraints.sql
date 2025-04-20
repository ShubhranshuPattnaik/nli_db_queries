USE `CORA`;

ALTER TABLE `cites`
ADD PRIMARY KEY (`cited_paper_id`, `citing_paper_id`);

ALTER TABLE `paper`
ADD PRIMARY KEY (`paper_id`);

ALTER TABLE `cites`
ADD CONSTRAINT `fk_cited_paper`
FOREIGN KEY (`cited_paper_id`) REFERENCES `paper`(`paper_id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `cites`
ADD CONSTRAINT `fk_citing_paper`
FOREIGN KEY (`citing_paper_id`) REFERENCES `paper`(`paper_id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `content`
ADD CONSTRAINT `fk_content_paper`
FOREIGN KEY (`paper_id`) REFERENCES `paper`(`paper_id`)
ON DELETE CASCADE ON UPDATE CASCADE;
