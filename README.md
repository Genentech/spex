<details open> <summary><b> System Requirements and Internet Connectivity</b></summary>

---

Before beginning the installation process, ensure your system meets the following requirements:

- **Storage Space:** A minimum of 70 GB of free disk space is required for installation and initial operations. It is recommended to have up to 150 GB of free space to accommodate future updates and data management needs.
- Better have 500gb (if yo need to look example data from lfs server )

- **Memory:** At least 16 GB of RAM is essential for smooth performance during installation and runtime.

- **Internet Connection:** A stable internet connection is necessary throughout the installation process and for initial task executions. This ensures timely downloads and updates.

- **3000, 80 Ports:** If, for some reason, ports are not open in Docker, you may need to open ports 80 and 3000 for Docker, or you might have to disable the firewall.

- In the Docker settings under Resources, set a minimum of **8 GB Memory** limit.

  <details><summary>Allow windows</summary>

  ![allow](workflow/images/allow.png)
  <details>
---
</details>

## Please note that the demo server includes large datasets, which may result in lengthy download times. The time required will depend on your network speed and stability, so if any step appears to stall, you may pause with `Control+C` and restart as needed to continue the download process.
<details open><summary>Datasets with which you can work are embedded in the repository at the links below</summary>
  <details><summary>IMC Tonsil</summary>

  - [IMC_Tonsil.ome.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/02/05-40-02.725/IMC_Tonsil.ome.tiff)
  </details>
  <details><summary>IMC PDAC</summary>

  - [IMC_PDAC_ROI1.ome.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/06/06-48-20.734/IMC_PDAC_ROI1.ome.tiff)
  - [IMC_PDAC_ROI2.ome.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/06/06-48-23.802/IMC_PDAC_ROI2.ome.tiff)
  - [IMC_PDAC_ROI3.ome.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/06/06-48-25.990/IMC_PDAC_ROI3.ome.tiff)
  - [IMC_PDAC_ROI4.ome.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/06/06-48-29.057/IMC_PDAC_ROI4.ome.tiff)
  </details>
  <details><summary>MIBI TNBC</summary>

  - [TA459_multipleCores2_Run-4_Point25.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-24-47.855/TA459_multipleCores2_Run-4_Point25.tiff)
  - [TA459_multipleCores2_Run-4_Point22.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-24-49.999/TA459_multipleCores2_Run-4_Point22.tiff)
  - [TA459_multipleCores2_Run-4_Point28.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-24-51.006/TA459_multipleCores2_Run-4_Point28.tiff)
  - [TA459_multipleCores2_Run-4_Point33.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-24-52.168/TA459_multipleCores2_Run-4_Point33.tiff)
  - [TA459_multipleCores2_Run-4_Point5.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-24-54.025/TA459_multipleCores2_Run-4_Point5.tiff)
  - [TA459_multipleCores2_Run-4_Point36.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-24-55.370/TA459_multipleCores2_Run-4_Point36.tiff)
  - [TA459_multipleCores2_Run-4_Point39.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-24-56.263/TA459_multipleCores2_Run-4_Point39.tiff)
  - [TA459_multipleCores2_Run-4_Point2.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-24-57.176/TA459_multipleCores2_Run-4_Point2.tiff)
  - [TA459_multipleCores2_Run-4_Point31.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-24-57.906/TA459_multipleCores2_Run-4_Point31.tiff)
  - [TA459_multipleCores2_Run-4_Point4.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-24-58.883/TA459_multipleCores2_Run-4_Point4.tiff)
  - [TA459_multipleCores2_Run-4_Point7.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-01.671/TA459_multipleCores2_Run-4_Point7.tiff)
  - [TA459_multipleCores2_Run-4_Point13.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-02.335/TA459_multipleCores2_Run-4_Point13.tiff)
  - [TA459_multipleCores2_Run-4_Point16.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-03.190/TA459_multipleCores2_Run-4_Point16.tiff)
  - [TA459_multipleCores2_Run-4_Point1.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-04.444/TA459_multipleCores2_Run-4_Point1.tiff)
  - [TA459_multipleCores2_Run-4_Point24.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-05.196/TA459_multipleCores2_Run-4_Point24.tiff)
  - [TA459_multipleCores2_Run-4_Point20.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-06.153/TA459_multipleCores2_Run-4_Point20.tiff)
  - [TA459_multipleCores2_Run-4_Point8.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-07.913/TA459_multipleCores2_Run-4_Point8.tiff)
  - [TA459_multipleCores2_Run-4_Point38.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-08.613/TA459_multipleCores2_Run-4_Point38.tiff)
  - [TA459_multipleCores2_Run-4_Point35.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-09.518/TA459_multipleCores2_Run-4_Point35.tiff)
  - [TA459_multipleCores2_Run-4_Point19.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-10.407/TA459_multipleCores2_Run-4_Point19.tiff)
  - [TA459_multipleCores2_Run-4_Point27.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-11.212/TA459_multipleCores2_Run-4_Point27.tiff)
  - [TA459_multipleCores2_Run-4_Point40.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-11.985/TA459_multipleCores2_Run-4_Point40.tiff)
  - [TA459_multipleCores2_Run-4_Point12.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-12.942/TA459_multipleCores2_Run-4_Point12.tiff)
  - [TA459_multipleCores2_Run-4_Point32.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-13.945/TA459_multipleCores2_Run-4_Point32.tiff)
  - [TA459_multipleCores2_Run-4_Point9.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-16.110/TA459_multipleCores2_Run-4_Point9.tiff)
  - [TA459_multipleCores2_Run-4_Point21.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-16.896/TA459_multipleCores2_Run-4_Point21.tiff)
  - [TA459_multipleCores2_Run-4_Point26.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-17.618/TA459_multipleCores2_Run-4_Point26.tiff)
  - [TA459_multipleCores2_Run-4_Point29.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-18.342/TA459_multipleCores2_Run-4_Point29.tiff)
  - [TA459_multipleCores2_Run-4_Point10.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-19.597/TA459_multipleCores2_Run-4_Point10.tiff)
  - [TA459_multipleCores2_Run-4_Point18.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-20.471/TA459_multipleCores2_Run-4_Point18.tiff)
  - [TA459_multipleCores2_Run-4_Point23.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-22.290/TA459_multipleCores2_Run-4_Point23.tiff)
  - [TA459_multipleCores2_Run-4_Point15.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-23.033/TA459_multipleCores2_Run-4_Point15.tiff)
  - [TA459_multipleCores2_Run-4_Point34.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-23.803/TA459_multipleCores2_Run-4_Point34.tiff)
  - [TA459_multipleCores2_Run-4_Point37.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-24.611/TA459_multipleCores2_Run-4_Point37.tiff)
  - [TA459_multipleCores2_Run-4_Point41.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-25.453/TA459_multipleCores2_Run-4_Point41.tiff)
  - [TA459_multipleCores2_Run-4_Point3.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-26.291/TA459_multipleCores2_Run-4_Point3.tiff)
  - [TA459_multipleCores2_Run-4_Point30.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-27.134/TA459_multipleCores2_Run-4_Point30.tiff)
  - [TA459_multipleCores2_Run-4_Point17.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-29.084/TA459_multipleCores2_Run-4_Point17.tiff)
  - [TA459_multipleCores2_Run-4_Point14.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-30.540/TA459_multipleCores2_Run-4_Point14.tiff)
  - [TA459_multipleCores2_Run-4_Point6.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-31.283/TA459_multipleCores2_Run-4_Point6.tiff)
  - [TA459_multipleCores2_Run-4_Point11.tiff](demo_data/omero_demo/omeroserver/OMERO/ManagedRepository/root_0/2024-10/11/09-25-32.003/TA459_multipleCores2_Run-4_Point11.tiff)
  </details>

- [MERFISH NSCLC.h5ad](demo_data/UPLOADS/161065100/merfish_lung.h5ad)
</details>


## SPEX Application Microservices and Architecture

### Core Repositories:
- **Full Application Package** (use submodules for easy cloning of all components):  
  [spex_bundle](https://github.com/Genentech/spex_bundle)

- **Backend**: [spex_backend](https://github.com/Genentech/spex_backend)
- **Frontend**: [spex_frontend](https://github.com/Genentech/spex_frontend)
- **Common Modules**: [spex_common](https://github.com/Genentech/spex_common)

### Microservices:
- **Image Downloader from Omero for Processing**: [spex_ms_omero_image_downloader](https://github.com/Genentech/spex_ms_omero_image_downloader)
- **Omero Session Management** (providing image information and API access): [spex_ms_omero_sessions](https://github.com/Genentech/spex_ms_omero_sessions)
- **Task Queue Manager**: [spex_ms_pipeline_manager](https://github.com/Genentech/spex_ms_pipeline_manager)
- **Script Execution and Environment Management**: [spex_ms_job_manager](https://github.com/Genentech/spex_ms_job_manager)

### Algorithms:
- **Data Clustering**: [spex_clustering](https://github.com/Genentech/spex_clustering)
- **Image Segmentation**: [spex_segmentation](https://github.com/Genentech/spex_segmentation)
- **Spatial Transcriptomics**: [spex_spatial_transcriptomics](https://github.com/Genentech/spex_spatial_transcriptomics)

These algorithms enable customization of data processing parameters and are integrated with the `spex_ms_job_manager` microservice for executing analytical tasks.

# Installation Guide

## Install Git LFS for Managing Large Files

<details><summary><b> Ubuntu</b></summary>

- Open Terminal and run:
```
sudo apt update
sudo apt install git-lfs
```
</details>

<details open><summary><b> Windows</b></summary>

- Download and install [Git for Windows](https://git-scm.com/download/win).
- if you have installed Git for Windows, you can check if running installs Git LFS:
- Open Powershell as administrator and run:
```
git lfs install
```
if you have this output:
```
Git LFS initialized.
```
![Lfs](workflow/images/1_1.png)


go to the next step [Bundle installation](#bundle-installation)
, if not
- Download and install [Git LFS](https://git-lfs.github.com/)
  follow the instructions for Windows installation.
</details>




<a id="bundle-installation"></a>
## Bundle Installation

- Go to the folder where you will deploy the project.
To navigate to a project folder in the terminal, you can use the cd command, which stands for "change directory."

```
cd my_project
```

- To set up Git LFS, open the terminal and run the following command:
```
git lfs install
```

- For the production bundle of the application, clone the repository:
```
git clone https://github.com/Genentech/spex_demo.git .

git lfs pull

```
- Wait for the process to complete. The total size of all downloaded project files should be around 10 gigabytes.
![clone](workflow/images/1_2.png)

<details>
  <summary><b>Set executable permissions (Ubuntu): </b></summary>

  ```
  chmod -R +x .
  ```
</details>

## Install Docker desktop on your Local Machine
- Download and install [Docker Desktop](https://www.docker.com/products/docker-desktop)

### Run application demo script:
<details> <summary><b>Ubuntu</b></summary>

- Execute the application demo script:
  ```
  ./app_demo.sh up
  ```
</details>

<details open> <summary><b>Windows</b></summary>

- Run the PowerShell script by command as administrator:
  ```
  PowerShell.exe -ExecutionPolicy Unrestricted -File .\app_demo.ps1 up
  ```

  ![run](workflow/images/1_3.png)
  <details><summary><b>windows 11 time to up</b></summary>
    
    ![win11timeline](workflow/images/w11timeline.png)
  </details>
</details>


Wait for the download to complete. If the download does not complete or hangs due to unstable connection, stop the process control+C and start the process again.

After the download is complete and the necessary images and containers are created, you should see 11 containers in the Docker application.

As a result, a browser window should open asking you to log in. If the page is not displayed? Try waiting 5-15 minutes and reload the page. Perhaps the containers have not all had time to collect yet.


**for open application you can start host "http://127.0.0.1:3000" in your browser,
at the first start, I would wait 5 minutes for the services to be initialized, such as the Omero server and frontend.**

for more information about SPEX can use

<details> <summary><b>Working workflow</b></summary>

- login in application use username **root** and password **omero**

![login](workflow/images/2_1.gif)

- ## create process
  To initiate a test process, first select Project 1 and click the **Analyze** button.
  Next, click the "Add Process" button, and enter the name of the process, such as "test".
  Then, access the process by clicking on it in the process list, and proceed to create the first task.
  ![create process](workflow/images/2_2.gif)
- ## create tasks
  Blocks can be connected to each other; the entry point is the choice of what we work with,
  an image or an anndata file. Subsequently, we select the following related blocks,
  which perform data transformation to achieve the desired result.
  ![create tasks](workflow/images/2_3.gif)
- ## run tasks
  All tasks are executed sequentially. You can start all tasks using the "Start ▶" button or the "Play ▶"
  button in each block. Also, you can delete a block if it is not needed.
  ![run tasks](workflow/images/2_4.gif)
  - ## Fix errors
  During the initial launch, related libraries are downloaded from the internet.
  If the internet connection is unstable, the installation may fail, indicated by a red flag over the task name.
  To reinitialize the installation or restart the task, you need to press the play button **▶** as shown below.
  ![errors](workflow/images/2_5.gif)
  - ## View results
  The results of the pipeline execution can be viewed in the review tab.
  If for some reason they are not displayed, you can request the data to be regenerated by pressing the
  "Delete zarr data" button and then the "Create zarr data" button.
  ![results](workflow/images/2_6.gif)
</details>