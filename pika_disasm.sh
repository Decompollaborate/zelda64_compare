./simpleDisasm.py ../hypdisasm/baserom/usa/boot.bin pikachu/boot  --vram 80000450 --functions ../hypdisasm/tables/usa/functions.csv --variables ../hypdisasm/tables/usa/variables.csv --file-splits ../hypdisasm/tables/usa/files_boot.csv --save-context pikachu/context_boot.txt
./simpleDisasm.py ../hypdisasm/baserom/usa/file_B3C70.bin  pikachu/file_B3C70   --vram 8010AAF0 --functions ../hypdisasm/tables/usa/functions.csv --variables ../hypdisasm/tables/usa/variables.csv --file-splits ../hypdisasm/tables/usa/files_file_B3C70.csv --save-context pikachu/context_B3C70.txt
./simpleDisasm.py ../hypdisasm/baserom/usa/file_DCF60.bin pikachu/file_DCF60   --vram 80133DE0 --functions ../hypdisasm/tables/usa/functions.csv --variables ../hypdisasm/tables/usa/variables.csv  --save-context pikachu/context_DCF60.txt
