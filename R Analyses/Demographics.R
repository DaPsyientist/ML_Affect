#MLSUI Demographics
### Load packages ###
if (!require("pacman")) {install.packages("pacman"); require("pacman")}
p_load(ggplot2, tidyr, tidyverse, sjPlot, performance, effects, 
       ggpubr, rstudioapi, R.matlab, car, brm, dplyr, brms, bayestestR)

### Loading and Cleaning Data ###
# Note: For this script to work, the data for encoding, subjectives, and recognition must be in
#   the same folder as this script
current_path <- getActiveDocumentContext()$path    # gets path for this R script
setwd(dirname(current_path)) # sets working directory to folder this R script is in

#Specify eligible participants
Eligible_Sample <- c('FC001', 'FC002', 'FC003', 'FC012', 'FC013', 'FC015', 'FC018', 'FC019', 'FC022', 'FC026','FC028','FC030','FC031','FC032','FC035', 'FC037', 'FC040', 'FC043', 'FC044', 'FC045', 'FC047', 'FC048', 'FC053', 'FC055', 'FC056', 'FC057', 'FC059', 'FC060', 'FC061', 'FC063', 'FC068', 'FC069', 'FC073', 'FC074', 'FC075', 'FC076', 'FC077', 'FC080', 'FC081', 'FC083', 'FC084', 'FC087', 'FC095', 'FC096', 'FC101', 'FC102', 'FC109', 'FC112', 'FC113', 'FC114', 'FC116', 'FC118', 'FC119', 'FC120', 'FC122', 'FC127', 'FC129', 'FC131', 'FC132', 'FC134', 'FC136', 'FC138', 'FC139', 'FC141', 'FC147', 'FC150', 'FC153', 'FC155', 'FC157', 'FC158', 'FC163', 'FC165', 'FC169', 'FC171', 'FC173', 'FC179', 'FC184', 'FC188', 'FC192', 'FC196', 'FC199', 'FC200', 'FC202', 'FC210', 'FC211', 'FC218', 'FC220', 'MGH001', 'MGH006', 'MGH007', 'MGH009', 'MGH010', 'MGH012', 'MGH013', 'MGH016', 'MGH017', 'MGH022', 'MGH023', 'MGH024', 'MGH025', 'MGH028', 'MGH029', 'MGH030', 'MGH032', 'MGH033', 'MGH035', 'MGH037', 'MGH038', 'MGH043', 'MGH046', 'MGH049', 'MGH051', 'MGH055', 'MGH058', 'MGH059', 'MGH060', 'MGH062', 'MGH063', 'MGH064', 'MGH066', 'MGH069', 'MGH070', 'MGH071', 'MGH073', 'MGH075', 'MGH076', 'MGH078', 'MGH079', 'MGH080', 'MGH081', 'MGH082', 'MGH087', 'MGH090', 'MGH091', 'MGH092', 'MGH093', 'MGH096', 'MGH113', 'MGH119', 'MGH121', 'MGH130', 'MGH132', 'MGH136', 'MGH139', 'MGH141','MGH150','MGH152','MGH154','MGH158', 'MGH211','MGH212')

#Load demographics data
Demo_MLSUI <- read_csv('./MLSUI_demographics.csv')

#Change variable type 
Demo_MLSUI$age_epic <- as.numeric(Demo_MLSUI$age_epic)

#Filter for eligible data
ML_Sample <- Demo_MLSUI %>% filter(ppt_id %in% Eligible_Sample)

## Calculate Summary Statistics ##
# Sex
ML_Sample %>% group_by(sex_epic) %>% summarize(count = n())

#Age
ML_Sample %>% summarize(avg = mean(age_epic, na.rm = TRUE), stdev = sd(age_epic, na.rm=TRUE)) #23.5 (12.9)
range(ML_Sample$age_epic, na.rm=TRUE) #12-69
