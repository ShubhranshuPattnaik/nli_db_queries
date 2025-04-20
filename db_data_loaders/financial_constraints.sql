USE `financial`;

ALTER TABLE `card`
ADD PRIMARY KEY (`card_id`);

ALTER TABLE `disp`
ADD PRIMARY KEY (`disp_id`);

ALTER TABLE `client`
ADD PRIMARY KEY (`client_id`);

ALTER TABLE `account`
ADD PRIMARY KEY (`account_id`);

ALTER TABLE `district`
ADD PRIMARY KEY (`district_id`);

ALTER TABLE `trans`
ADD PRIMARY KEY (`trans_id`);

ALTER TABLE `order`
ADD PRIMARY KEY (`order_id`);

ALTER TABLE `loan`
ADD PRIMARY KEY (`loan_id`);


ALTER TABLE `card`
ADD CONSTRAINT `fk_card_disp`
FOREIGN KEY (`disp_id`) REFERENCES `disp`(`disp_id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `disp`
ADD CONSTRAINT `fk_disp_client`
FOREIGN KEY (`client_id`) REFERENCES `client`(`client_id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `disp`
ADD CONSTRAINT `fk_disp_account`
FOREIGN KEY (`account_id`) REFERENCES `account`(`account_id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `trans`
ADD CONSTRAINT `fk_trans_account`
FOREIGN KEY (`account_id`) REFERENCES `account`(`account_id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `order`
ADD CONSTRAINT `fk_order_account`
FOREIGN KEY (`account_id`) REFERENCES `account`(`account_id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `loan`
ADD CONSTRAINT `fk_loan_account`
FOREIGN KEY (`account_id`) REFERENCES `account`(`account_id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `client`
ADD CONSTRAINT `fk_client_district`
FOREIGN KEY (`district_id`) REFERENCES `district`(`district_id`)
ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE `account`
ADD CONSTRAINT `fk_account_district`
FOREIGN KEY (`district_id`) REFERENCES `district`(`district_id`)
ON DELETE CASCADE ON UPDATE CASCADE;
