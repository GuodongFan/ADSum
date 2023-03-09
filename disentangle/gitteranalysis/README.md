# An Empirical Study of Developer Discussions in Gitter Platform #

**Requirements**
* Python 2.7 or newer
* R 3.1 or newer

**Dataset**

The full dataset is hosted on [Onedrive](https://queensuca-my.sharepoint.com/:f:/g/personal/18oe3_queensu_ca/Eu-imCR9xohNgwJD3edzYzsBVlgx6h-9N92tpgfe_Ty0_g?e=ls38OJ)

*  **gitter_archive** contains the JSON format data for all 856 chatrooms. Each folder in gitter_archive contains the JSON files for each chatroom.
*  **full_data.csv** contains all the chatroom data in csv format.
*  **all_threads.csv** contains all the identified threads for the full dataset.

**Files description**
*  **data** folder contains the sample data for chatroom data and the identified threads that are already present in the Onedrive link.
    * **full_data_sample.csv** contains the sample of chatroom data.
    * **all_threads_sample.csv** contains the sample of the identified threads.
*  **python scripts** folder contains the scripts for thread identification.
    * **thread_identification.py** contains the algorithm for thread identification.


For any questions, please send email to osama.ehsan@queensu.ca