# Chronos: Exploiting Time-Side Channels to Uncover Firmware Versions in Network Devices

## Introduction:
This project is an online detection-based implicit information firmware version identification system, which includes a detection module, a crawling module, a data analysis module, and a fingerprint generation module.

## Data_analysis_module
This module is mainly used for data analysis and preprocessing, such as:
1. Detection data processing and reconstruction
2. LMT extraction and normalization
3. ERT reconstruction and database construction
4. Data clustering, implementation of bimodal feature-based model clustering algorithm
5. Data statistical feature analysis, implementation of statistical feature-based file selection algorithm


## Finger_generation_mudule
This module is mainly used for fingerprint generation and version identification testing, realizing the time-driven version fingerprint algorithm to apply time-constrained mapping of LMT and ERT, automatically generating fine-grained firmware version fingerprint.
### ERT_data_test
The ERT data scraped from the manufacturer’s official websites.
### test_data_lmt
The LMT data collected. Since the complete original data may expose the device IP and cause security risks, we only provide processed data for testing.

## Spider_module
This module is used to implement ERT crawling and preprocessing, crawl multiple official pages of mainstream manufacturers, and combine Scrapy and Selenium to realize information collection for ERT database construction.

## Dscan_module
This module is mainly used to implement in-depth detection of device IP, collect device homepage information and all its static resources, as well as device-related information disclosed from other protocol ports and special paths. This tool is commercially available and therefore cannot be made public.

The Deep_scan module is primarily used for new data collection, and the absence of this module does not affect the implementation of the core fingerprint generation algorithm in our code base.
 
Nevertheless, to facilitate better academic communication, while we cannot directly disclose the deep_scan tool on GitHub, we can provide an alternative method to achieve static resource collection. By combining public internet search engines such as Shodan, Fofa, and Cydar to obtain target device IP addresses and ports, and using our improved URL-finder tool, we can capture all JS and CSS files. This approach achieves near-deep_scan performance for new data mining. The relevant tools have been updated on our GitHub.

Additionally, for academic research needs or collaboration opportunities, we can provide a demo version of deep_scan via email for academic research. To ensure anonymity and fairness during the paper review process, the email address will be updated after the review is completed.

To run URL_finder_scanning, simply navigate to the folder where the .exe file is located, and enter the target IP and port from which you want to capture static resources.
Example command: 
`.\URLFinder-windows_scanning.exe -u https://71.183.100.57:5001/ -s all -m 3 -o`
- `-s all` means to capture all static resource files.
- `-m 3` means to recursively crawl up to 3 layers of URLs.
- `-o` specifies the output file path.
