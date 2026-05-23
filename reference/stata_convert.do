//2014 data clean

use "$cfps2014/cfps2014_adult.dta", clear
keep pid kr1 kr4  qc201 ks801code cfps2014_age kra402
for var _all: replace X =. if inlist(X, -10, -9, -8, -2, -1, 79)

keep if kr1 == 4

gen voc = 1 if kr4 == 3 | kr4==5 |kr4==6
replace voc = 0 if kr4==1
label define vocno 1 "职业教育" 0 "普通高中"
label values voc vocno
label variable voc "是否上职校"
drop kr4

gen grade = 2014 - kra402
replace grade = 1 if grade == 0
replace grade = 3 if grade >3

label variable grade 当前年级
label define gradenum 1 "高一" 2 "高二" 3 "高三"
label values grade gradenum

gen edu_asp = qc201
replace edu_asp =. if edu_asp ==0
replace edu_asp = 0 if edu_asp  ==1
replace edu_asp = 0 if edu_asp  ==9
replace edu_asp = 23 if edu_asp  ==8
replace edu_asp = 19 if edu_asp  ==7
replace edu_asp = 16 if edu_asp  ==6
replace edu_asp = 15 if edu_asp  ==5
replace edu_asp = 12 if edu_asp  ==4
replace edu_asp = 9 if edu_asp  ==3
replace edu_asp = 6 if edu_asp  ==2
label define eduaspnum 0 "不需念书" 6 "小学" 9 "初中" 12 "高中" 15 "大专" 16 "本科" 19 "硕士" 23 "博士" 
label values edu_asp eduaspnum
label variable edu_asp "教育期望年限"
drop qc201

gen isso_asp = 1100 if  ks801code == 1
replace isso_asp = 1200 if  ks801code == 2
replace isso_asp = 2100 if  ks801code == 3
replace isso_asp = 2140 if  ks801code == 4
replace isso_asp = 3140 if  ks801code == 5
replace isso_asp = 2220 if  ks801code == 6
replace isso_asp = 3410 if  ks801code == 7
replace isso_asp = 2420 if  ks801code == 8
replace isso_asp = 2300 if  ks801code == 9
replace isso_asp = 2450 if  ks801code == 10
replace isso_asp = 3475 if  ks801code == 11
replace isso_asp = 2451 if  ks801code == 12
replace isso_asp = 2000 if  ks801code == 13
replace isso_asp = 4110 if  ks801code == 14
replace isso_asp = 5160 if  ks801code == 15
replace isso_asp = 5132 if  ks801code == 16
replace isso_asp = 5112 if  ks801code == 17
replace isso_asp = 5132 if  ks801code == 18
replace isso_asp = 6100 if  ks801code == 19
replace isso_asp = 7230 if  ks801code == 20
replace isso_asp = 8300 if  ks801code == 21
replace isso_asp = 8000 if  ks801code == 22
replace isso_asp = . if  ks801code == 23
replace isso_asp = . if  ks801code == 24
replace isso_asp = . if  ks801code == 25
replace isso_asp = 9000 if  ks801code == 26
replace isso_asp = . if  ks801code == 27
replace isso_asp = 9000 if  ks801code == 28
replace isso_asp = . if  ks801code == 29
iskoisei isei_asp, isko(isso_asp)
drop ks801code isso_asp

