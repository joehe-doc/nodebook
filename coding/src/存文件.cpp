#include <fstream>
using namespace std;

ofstream out;
out.open("C:\\temp_2.mp4",ios::binary|ios::app);
out.write((char*)pBuffer,dwBufSize);
out.close();