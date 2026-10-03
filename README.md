# Mass adding of books to a shelf in calibre-web (MABS)

## What

A Python script to add books to a calibre-web shelf in bulk.<br>
一个Python脚本，用于批量向calibre-web书架添加书籍。

## ~~Why~~

## How

1. export a list of books from calibre to a csv file (e.g. `my books.csv`) [optional].<br>导出calibre中的书籍列表到一个csv文件（例如`我的书籍.csv`）[可选]。
   1. `Menu convert books` -> `create a catalog of the books in your calibre library`<br>`菜单 转换书籍` -> `为calibre书库中的书籍编制书目`
2. filter the required book IDs<br>筛选需要的书籍id
3. edit `.env` file<br>编辑`.env`文件

```ini
# lang = "en"
username = 'admin'
password = 'admin123'
server = 'http://127.0.0.1:8083'
booklist = 'my books.csv'
```

4. make sure calibre-web is running<br>确保calibre-web正在运行
5. activate the virtual environment,insstall dependencies<br>激活虚拟环境，安装依赖

```bash
python -m venv .venv
source .venv\Scripts\activate
pip install -r requirements.txt
```

6. run `python mabs.py`<br>运行`python mabs.py`

## Related

- [`calibre`](https://calibre-ebook.com/)
- [`janeczku`/`calibre-web`](https://github.com/janeczku/calibre-web)
- [`OzzieIsaacs`/`cps-shelf-adder`](https://github.com/OzzieIsaacs/cps-shelf-adder)

## Keywords

> calibre, calibre-web, shelf, add <br> 书架, 添加

## License

[MIT](LICENSE)
