# Mindreading
Django project for book recommendation website using [Distributed Heterogeneous RBM](https://github.com/leee5495/Distributed_Heterogeneous_RBM)

### How to run
1. download data and model from [here](https://drive.google.com/drive/folders/12QRYrRv2_1wTrJcaAekISDgaawMz64z4?usp=sharing)
    - unzip `data.zip` to `./data`
    - unzip `model.zip` to `./model`
  
2. run `db_update.py` script
   - ``` python
     # open django shell
     $ python manage.py shell
     ```
    - run `db_update.py` line by line in python shell
   
   OR download `mydatabase.zip` from [here](https://drive.google.com/drive/folders/12QRYrRv2_1wTrJcaAekISDgaawMz64z4?usp=sharing) and unzip `mydatabase` to the root directory (recommended)
  
3. launch django server
   ``` python
   # launch django server
   $ python manage.py runserver
   ```
