import os


with open('eventList_THQ_3l.txt', 'r') as file1:
    with open('eventList_THQ_3l_ttHCuts.txt', 'r') as file2:
        overlap = set(file1).intersection(file2)

overlap.discard('\n')

with open('overlap_THQ_Sample_3l.txt', 'w') as file_out:
    for line in overlap:
        file_out.write(line)


with open('eventList_TTHnobb_mWCutfix_ext_LHE_3l.txt', 'r') as file3:
    with open('eventList_TTHnobb_mWCutfix_ext_LHE_3l_ttHCuts.txt', 'r') as file4:
        overlap2 = set(file3).intersection(file4)

overlap2.discard('\n')

with open('overlap_TTH_sample_3l.txt', 'w') as file_out2:
    for line in overlap2:
        file_out2.write(line)

####2lss
##mumu

with open('eventList_THQ_2lss_mumu.txt', 'r') as file1:
    with open('eventList_THQ_2lss_mumu_ttHCuts.txt', 'r') as file2:
        overlap = set(file1).intersection(file2)

overlap.discard('\n')

with open('overlap_THQ_Sample_2lss_mumu.txt', 'w') as file_out:
    for line in overlap:
        file_out.write(line)


with open('eventList_TTHnobb_mWCutfix_ext_LHE_2lss_mumu.txt', 'r') as file3:
    with open('eventList_TTHnobb_mWCutfix_ext_LHE_2lss_mumu_ttHCuts.txt', 'r') as file4:
        overlap2 = set(file3).intersection(file4)

overlap2.discard('\n')

with open('overlap_TTH_sample_2lss_mumu.txt', 'w') as file_out2:
    for line in overlap2:
        file_out2.write(line)


##emu

with open('eventList_THQ_2lss_emu.txt', 'r') as file1:
    with open('eventList_THQ_2lss_emu_ttHCuts.txt', 'r') as file2:
        overlap = set(file1).intersection(file2)

overlap.discard('\n')

with open('overlap_THQ_Sample_2lss_emu.txt', 'w') as file_out:
    for line in overlap:
        file_out.write(line)


with open('eventList_TTHnobb_mWCutfix_ext_LHE_2lss_emu.txt', 'r') as file3:
    with open('eventList_TTHnobb_mWCutfix_ext_LHE_2lss_emu_ttHCuts.txt', 'r') as file4:
        overlap2 = set(file3).intersection(file4)

overlap2.discard('\n')

with open('overlap_TTH_sample_2lss_emu.txt', 'w') as file_out2:
    for line in overlap2:
        file_out2.write(line)

##ee

with open('eventList_THQ_2lss_ee.txt', 'r') as file1:
    with open('eventList_THQ_2lss_ee_ttHCuts.txt', 'r') as file2:
        overlap = set(file1).intersection(file2)

overlap.discard('\n')

with open('overlap_THQ_Sample_2lss_ee.txt', 'w') as file_out:
    for line in overlap:
        file_out.write(line)


with open('eventList_TTHnobb_mWCutfix_ext_LHE_2lss_ee.txt', 'r') as file3:
    with open('eventList_TTHnobb_mWCutfix_ext_LHE_2lss_ee_ttHCuts.txt', 'r') as file4:
        overlap2 = set(file3).intersection(file4)

overlap2.discard('\n')

with open('overlap_TTH_sample_2lss_ee.txt', 'w') as file_out2:
    for line in overlap2:
        file_out2.write(line)



#######data
##3l

with open('eventList_THQcuts_data_3l.txt', 'r') as file1:
    with open('eventList_data_3l_ttHCuts.txt', 'r') as file2:
        overlap = set(file1).intersection(file2)

overlap.discard('\n')

with open('overlap_data_3l.txt', 'w') as file_out:
    for line in overlap:
        file_out.write(line)


## 2lss ee

with open('eventList_THQcuts_data_2lss_ee.txt', 'r') as file3:
    with open('eventList_data_2lss_ee_ttHCuts.txt', 'r') as file4:
        overlap2 = set(file3).intersection(file4)

overlap2.discard('\n')

with open('overlap_data_2lss_ee.txt', 'w') as file_out2:
    for line in overlap2:
        file_out2.write(line)

## 2lss emu

with open('eventList_THQcuts_data_2lss_emu.txt', 'r') as file3:
    with open('eventList_data_2lss_emu_ttHCuts.txt', 'r') as file4:
        overlap2 = set(file3).intersection(file4)

overlap2.discard('\n')

with open('overlap_data_2lss_emu.txt', 'w') as file_out2:
    for line in overlap2:
        file_out2.write(line)

## 2lss mumu

with open('eventList_THQcuts_data_2lss_mumu.txt', 'r') as file3:
    with open('eventList_data_2lss_mumu_ttHCuts.txt', 'r') as file4:
        overlap2 = set(file3).intersection(file4)

overlap2.discard('\n')

with open('overlap_data_2lss_mumu.txt', 'w') as file_out2:
    for line in overlap2:
        file_out2.write(line)





# eventList_THQ_2lss_THQcuts=['eventList_THQ_2lss_mumu.txt','eventList_THQ_2lss_ee.txt','eventList_THQ_2lss_emu.txt']
# eventlist_TTH_2lss_THQcuts=['eventList_TTHnobb_mWCutfix_ext_LHE_2lss_mumu.txt','eventList_TTHnobb_mWCutfix_ext_LHE_2lss_ee.txt','eventList_TTHnobb_mWCutfix_ext_LHE_2lss_emu.txt']
# eventList_THQ_2lss_TTHcuts=['eventList_THQ_2lss_mumu_ttHCuts.txt','eventList_THQ_2lss_ee.txt','eventList_THQ_2lss_emu_ttHCuts.txt']  
# eventList_TTH_2lss_TTHcuts=['eventList_TTHnobb_mWCutfix_ext_LHE_2lss_mumu_ttHCuts.txt','eventList_TTHnobb_mWCutfix_ext_LHE_2lss_ee_ttHCuts.txt','eventList_TTHnobb_mWCutfix_ext_LHE_2lss_emu_ttHCuts.txt']

# for index, elist in eventList_THQ_2lss_THQcuts:
#     with open('elist', 'r') as file_1:
#         with open(eventList_THQ_2lss_TTHcuts[index], 'r') as file_2:
#             overlap = set(file_1).intersection(file_2)

        
#     overlap.discard('\n')
    
#     with open('overlap_THQ_Sample_something.txt', 'w') as file_out:
#         for line in overlap:
#             file_out.write(line)
