Lab for writing pyserial scripts for reading and binning Faraday cup (and other) current measurements at the MC40 cyclotron

clone and install pyserial (in your env with pip in it):
```
git clone https://github.com/louisbutt338/serial_lab.git
cd serial_lab
pip install pyserial
```

run python version:
```
python pyserial/read_current.py 
```

run c++ version
```
cmake -S src -B build
cmake --build build
./build/serial_posix 
```
