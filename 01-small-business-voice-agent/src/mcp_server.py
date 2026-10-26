from fastmcp import FastMCP

from src.tools import check_product_stock

mcp=FastMCP("Small Business Assistant")

@mcp.tool
def get_product_stock(product_id:str)->dict:
    return check_product_stock(product_id)

if __name__ == "__main__":
    mcp.run()