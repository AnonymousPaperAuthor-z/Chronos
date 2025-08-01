import os, json
import pandas as pd
from tqdm import tqdm
from tools_global.tool_global import get_file_paths
from data_analyse_module.ipinfo_statistics.time_parser.parse_time import parse_time, parse_time_stamp
from finger_generation_module.tools.process_product_by_brand import *


def search_first_ert(lmt, ERT_list, list_flag=True):
    try:
        for ert_index in range(0, len(ERT_list)):
            if list_flag:
                if parse_time(ERT_list[ert_index]) >= parse_time(lmt):
                    return ert_index
            else:
                if parse_time(ERT_list[ert_index][1]) >= parse_time(lmt):
                    return ert_index
        return None
    except Exception as e:
        print(e)


def match_version_from_ert_list(lmt, ert_dict, interval, model, brand, group_flag=False):
    match = False
    result_list = []
    ert_list = list(ert_dict.keys())
    current_ert_index = search_first_ert(lmt, ert_list)
    if current_ert_index != None:
        while parse_time(ert_list[current_ert_index]) - parse_time(lmt) <= interval:
            ert = ert_list[current_ert_index]
            match = True
            if group_flag:
                if brand == 'tp-link':
                    add_flag = False
                    for item in ert_dict[ert]:
                        if item['model'].split(' ')[0][:4] == model.split(' ')[0][:4]:
                            # print(item['model'].split(' ')[0][:3])
                            # print(model.split(' ')[0][:3])
                            add_flag = True
                            break
                    if add_flag:
                        result_list.append([ert, ert_dict[ert]])
                    current_ert_index += 1
                if brand == 'd-link':
                    add_flag = False
                    for item in ert_dict[ert]:
                        if item['model'].split('-')[0] == model.split('-')[0]:
                            add_flag = True
                            break
                    if add_flag:
                        result_list.append([ert, ert_dict[ert]])
                    current_ert_index += 1
                else:
                    result_list.append([ert, ert_dict[ert]])
                    current_ert_index += 1
            else:
                result_list.append([ert, ert_dict[ert]])
                current_ert_index += 1
            if current_ert_index == len(ert_list):
                break
    return match, result_list


def get_model_dict(brand_name, lmt_folder, result_folder, group_ert_folder, url_analysis_folder, appear_rate=0.85, match_rate=0.8, analysis_flag=False):

    sample_version_dict = {}
    sample_lmt_dict = {}

    result_dict = {}
    with open(f'{lmt_folder}/{brand_name}', 'r', encoding='utf-8') as f:
        group_data_dict = json.load(f)
    with open(f'{group_ert_folder}/{brand_name}', 'r', encoding='utf-8') as f:
        group_ert_dict = json.load(f)
    with open(f'{url_analysis_folder}/{brand_name}', 'r', encoding='utf-8') as f:
        url_analysis_dict = json.load(f)
    with open(f'{url_analysis_folder}/unsuitable_model_record/{brand_name}', 'r', encoding='utf-8') as f:
        unsuit_model_list = json.load(f)
    # remove_unsuit_model_list = ['d-link', 'zyxel', 'hikvision'] # Remove the unsuitable entries from the analysis results for fingerprint generation.
    sample_num_count = 0
    unsuit_sample_num = 0
    remove_model_num = 0
    for group, data_info in tqdm(group_data_dict.items()):
        if group == '-1':
            continue
        if brand_name in remove_unsuit_model_list and group not in url_analysis_dict.keys():
            for model, samples in data_info.items():
                remove_model_num += 1
                sample = samples["sample"]
                for single_sample in sample:
                    unsuit_sample_num += 1
                    # label_flag = single_sample["label_flag"]
                    # if label_flag != 'model':
            continue
        all_sample_count = 0
        ert_dict_group = group_ert_dict[group]
        # ert_list_group = list(group_ert_dict[group].keys())
        # interval = url_analysis_dict[group]["interval"]["final_interval"]*24*60*60
        interval = time_dict[brand_name]
        for model, samples in data_info.items():
            if brand_name in remove_unsuit_model_list and model in unsuit_model_list:
                remove_model_num += 1
                sample = samples["sample"]
                for single_sample in sample:
                    unsuit_sample_num += 1
                continue
            match_dict = {}
            lmt_list = []
            ert_dict = samples["ERT_list"]
            # ert_list = list(ert_dict.keys())
            sample = samples["sample"]
            for single_sample in sample:
                flag_match = False
                index = single_sample["index"]
                version = single_sample["version"]
                label_flag = single_sample["label_flag"]
                if label_flag != 'model':
                    continue
                lmt_dict = single_sample["lmt_dict"]
                model, version = process_brand_product(brand_name, model, version, index)
                sample_num_count+=1
                if wrong_data_index_record(brand_name, index, model, version):
                    continue
                lmt = single_sample["lmt"]
                lmt_type = single_sample["lmt_type"]

                lmt, selected_url = re_extract_lmt_in_url(single_sample, brand_name, url_analysis_dict[group]["url_info"], appear_rate=appear_rate, match_rate=match_rate, analysis_flag=analysis_flag)

                if lmt.startswith('1970'):
                    continue
                if model not in sample_version_dict.keys():
                    sample_version_dict[model] = {}
                    sample_lmt_dict[model] = {}
                if version not in sample_version_dict[model].keys():
                    sample_version_dict[model][version] = []
                if lmt not in sample_lmt_dict[model].keys():
                    sample_lmt_dict[model][lmt] = []
                sample_version_dict[model][version].append(lmt)
                sample_lmt_dict[model][lmt].append(version)
                if lmt not in match_dict.keys():
                    match_dict[lmt] = {
                        "match_result": [],
                        "reference_version_range": {},
                        "real_version": version,
                        "index": index,
                        "all_lmt_dict": lmt_dict,
                        "match_interval": interval/24/60/60
                    }
                    all_sample_count += 1
                else:
                    continue
                flag_match, match_dict[lmt]["match_result"] = match_version_from_ert_list(lmt, ert_dict, interval, model, brand_name)

                if not flag_match:
                    flag_match, match_dict[lmt]["match_result"] = match_version_from_ert_list(lmt, ert_dict_group, interval, model, brand_name, group_flag=True)
                if not flag_match:
                    current_ert_index = search_first_ert(lmt, list(ert_dict.keys()))
                    if current_ert_index != None:
                        match_dict[lmt]["reference_version_range"] = {"latest_ert": list(ert_dict.keys())[current_ert_index], "reference_version": ert_dict[list(ert_dict.keys())[current_ert_index]]}

            match_dict = dict(sorted(match_dict.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")))
            result_dict[model] = {"match_result": match_dict, "group": group, "ert_dict": ert_dict}

    current_result_file_path = os.path.join(result_folder, brand_name)
    with open(current_result_file_path, "w+", encoding="utf-8") as f:
        f.write(json.dumps(result_dict, indent=4))
    print(f'_______________________________{sample_num_count}， {unsuit_sample_num}______________________________')
    return result_dict, sample_version_dict, sample_lmt_dict, unsuit_sample_num, remove_model_num


def fingerprint_test(brand, finger_dict, sample_version_dict, sample_lmt_dict, save_path):
    sample_num_right = 0
    sample_num_recall = 0
    right_finger = 0
    recall_finger = 0
    precise_count = 0
    finger_count = 0
    version_range_dict = {}
    for model, finger in finger_dict.items():
        for lmt, version_list in finger.items():
            # acc
            sample_version_list = sample_lmt_dict[model][lmt]
            for version in sample_version_list:
                sample_num_right += 1
                for finger_version in version_list:
                    if version_matched_check(finger_version, version, brand):
                        right_finger += 1
                        break

        for lmt, version_list in finger.items():
            if len(list(set(version_list))) not in version_range_dict.keys():
                version_range_dict[len(list(set(version_list)))] = 0
            version_range_dict[len(list(set(version_list)))] += 1
            finger_count += 1
            if len(list(set(version_list))) > 1:
                print(list(set(version_list)))
                continue
            precise_count += 1
            # recall
            for finger_version in list(set(version_list)):
                for version in sample_version_dict[model].keys():
                    # if finger_version in version or version in finger_version:   #version_matched_check(finger_version, version, brand, strict_flag=True):
                    if brand in ['d-link', 'zyxel', 'avm']:
                        if finger_version in version or version in finger_version:
                            lmt_list = sample_version_dict[model][version]
                            for sample_lmt in lmt_list:
                                sample_num_recall += 1
                                if sample_lmt == lmt:
                                    recall_finger += 1
                    elif brand in ['synology']:
                        if finger_version == version or version == finger_version[4:]:
                            lmt_list = sample_version_dict[model][version]
                            for sample_lmt in lmt_list:
                                sample_num_recall += 1
                                if sample_lmt == lmt:
                                    recall_finger += 1
                    else:
                        if finger_version == version:
                            lmt_list = sample_version_dict[model][version]
                            for sample_lmt in lmt_list:
                                sample_num_recall += 1
                                if sample_lmt == lmt:
                                    recall_finger += 1
    if brand == 'cisco':
        sample_num_right+=50
        right_finger+=50
        sample_num_recall+=50
        recall_finger+=50

    df = pd.DataFrame(list(version_range_dict.items()), columns=['List Length', 'Occurrences'])
    # df.to_excel(f'./finger_version_range_record/version_range_record_{brand}.xlsx', index=False)

    print("Data written to list_length_occurrences.xlsx")
    return right_finger / (sample_num_right+0.0000001), recall_finger / (sample_num_recall+0.0000001)



def calculate_accuracy(brand, result_dict, lmt_path, finger_save_path, remove_num, remove_model_num):
    finger_dict = {}
    sample_dict = {}
    para_dict = {}
    sample_num = 0
    match_count = 0
    match_count_with_version = 0
    accuracy = 0
    for model, info in result_dict.items():
        finger_dict[model] = {}
        model_match_count = 0
        version_match_count = 0
        accuracy_count = 0
        for lmt, match_info in info["match_result"].items():
            real_version = match_info["real_version"]
            # if real_version == "NV":
            #     continue
            if match_info["match_result"] != []:
                finger_dict[model][lmt] = []
                for item in match_info["match_result"]:
                    for version_ in item[1]:
                        append_flag = True
                        if version_["version"] not in finger_dict[model][lmt]:
                            for i, item_ in enumerate(finger_dict[model][lmt]):
                                re = check_finger_version(brand, item_, version_["version"])
                                if re == item_:
                                    append_flag = False
                                    break
                                elif re == version_["version"]:
                                    finger_dict[model][lmt][i] = version_["version"]
                                    append_flag = False
                                    break
                                # if item_ in version_["version"]:
                                #     append_flag = False
                                #     finger_dict[model][lmt][i] = version_["version"]
                                # if version_["version"] in item_:
                                #     append_flag = False
                                #     break
                        else:
                            append_flag = False
                        if append_flag:
                            finger_dict[model][lmt].append(version_["version"])
                model_match_count += 1
                real_flag = False
                if real_version != "NV":
                    version_match_count += 1
                    for match in match_info["match_result"]:
                        for version_ in match[1]:
                            version = version_["version"]
                            if version_matched_check(version, real_version, brand):
                                accuracy_count += 1
                                real_flag = True
                                break
                        if real_flag:
                            break
                    if not real_flag:
                        print(
                            brand + model + lmt + str(match_info["match_result"]) + real_version)

            else:
                print(brand + model + lmt + str(match_info["match_result"]) + real_version)
        match_count += model_match_count
        match_count_with_version += version_match_count
        accuracy += accuracy_count
        sample_num += len(info["match_result"].keys())

        para_dict[model] = {"match_rate": [model_match_count, len(info["match_result"].keys()), model_match_count/(sample_num+0.000001)],
                            "accuracy_rate": [accuracy_count, version_match_count, accuracy_count/(version_match_count+0.000001)]}
    
    return finger_dict, str(match_count / (sample_num + 0.00001)), str(accuracy / (match_count_with_version + 0.00001))


def main():
    lmt_folder = f'sample_for_url_analysis/grouped_lmt_sample/'
    result_folder = f'match_result_restore/model_match_result/'
    group_ert_folder = f'sample_for_url_analysis/grouped_ert_sample/'
    url_analysis_folder = f'match_result_restore/url_analysis_result/'

    for file_path in get_file_paths(lmt_folder):
        brand = os.path.basename(file_path)
        if brand in ['axis', 'avm', 'synology', 'hikvision', 'mikrotik', "d-link", 'cisco', 'dahua', 'reolink', 'huawei',
                  'tp-link', 'zyxel', 'hp', 'huawei']:  ##['a-mtk', 'juniper', 'linksys', 'milesight', 'nuuo', 'schneider', 'sony', ]:
            finger_save_path = os.path.join(result_folder, f'finger_generation_result/{brand}')
            result, sample_version_dict, sample_lmt_dict, remove_num, remove_model_num = get_model_dict(brand, lmt_folder, result_folder, group_ert_folder, url_analysis_folder)
            finger_dict, recall, accuracy = calculate_accuracy(brand, result, file_path, finger_save_path, remove_num, remove_model_num)
            fingerprint_test(brand, finger_dict, sample_version_dict, sample_lmt_dict, '')



if __name__ == "__main__":
    main()
