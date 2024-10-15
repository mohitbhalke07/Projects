import scrapy

class ProductSpider(scrapy.Spider):
  name = "products_scrap"
  start_urls = [
                "https://www.flipkart.com/audio-video/speakers/pr?sid=0pm%2C0o7&otracker=categorytree&p%5B%5D=facets.type%255B%255D%3DHome%2BTheatre&otracker=nmenu_sub_Electronics_0_Home+Theatres&p%5B%5D=facets.type%255B%255D%3DTower%2BSpeaker&p%5B%5D=facets.type%255B%255D%3DSoundbar&p%5B%5D=facets.brand%255B%255D%3DboAt&p%5B%5D=facets.brand%255B%255D%3DJBL&p%5B%5D=facets.brand%255B%255D%3DSONY&p%5B%5D=facets.brand%255B%255D%3DMivi", 
                "https://www.flipkart.com/search?q=microwave+oven&sid=j9e%2Cm38%2Co49&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_1_10_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_10_na_na_na&as-pos=1&as-type=RECENT&suggestionId=microwave+oven%7CMicrowave+Ovens&requestId=7786a822-b9b3-433c-8d4c-008ae2772f8d&as-backfill=on&otracker=nmenu_sub_TVs+%26+Appliances_0_Microwave+Ovens&p%5B%5D=facets.brand%255B%255D%3DLG&p%5B%5D=facets.brand%255B%255D%3DSAMSUNG&p%5B%5D=facets.brand%255B%255D%3DIFB&p%5B%5D=facets.brand%255B%255D%3DPanasonic",
                "https://www.flipkart.com/search?q=television&sid=ckf%2Cczl&as=on&as-show=on&otracker=AS_QueryStore_OrganicAutoSuggest_1_6_na_na_na&otracker1=AS_QueryStore_OrganicAutoSuggest_1_6_na_na_na&as-pos=1&as-type=RECENT&suggestionId=television%7CTelevisions&requestId=65b47484-4dce-4e5d-bc6c-ff152591e1f1&as-searchtext=television&p%5B%5D=facets.brand%255B%255D%3DSONY&p%5B%5D=facets.brand%255B%255D%3DLG&p%5B%5D=facets.brand%255B%255D%3DSAMSUNG&p%5B%5D=facets.brand%255B%255D%3DMi&p%5B%5D=facets.brand%255B%255D%3DPanasonic"
                "https://www.flipkart.com/search?q=laptops&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&p%5B%5D=facets.brand%255B%255D%3DLenovo&p%5B%5D=facets.brand%255B%255D%3DApple&p%5B%5D=facets.brand%255B%255D%3DHP&p%5B%5D=facets.brand%255B%255D%3DASUS&p%5B%5D=facets.brand%255B%255D%3DDELL&p%5B%5D=facets.brand%255B%255D%3DMSI",
                "https://www.flipkart.com/search?q=mobiles&as=on&as-show=on&otracker=AS_Query_TrendingAutoSuggest_1_0_na_na_na&otracker1=AS_Query_TrendingAutoSuggest_1_0_na_na_na&as-pos=1&as-type=TRENDING&suggestionId=mobiles&requestId=e2c0a9e3-6634-49de-b1c2-6d577cf43fbf&p%5B%5D=facets.brand%255B%255D%3DApple&p%5B%5D=facets.brand%255B%255D%3DSAMSUNG&p%5B%5D=facets.brand%255B%255D%3DGoogle&p%5B%5D=facets.brand%255B%255D%3Dvivo&p%5B%5D=facets.brand%255B%255D%3DNokia&p%5B%5D=facets.brand%255B%255D%3DOnePlus&p%5B%5D=facets.brand%255B%255D%3DSONY&p%5B%5D=facets.brand%255B%255D%3DOPPO&p%5B%5D=facets.brand%255B%255D%3DPOCO"
                ]

  def parse(self, response):

    product_detail_links = response.xpath('//div[@class="cPHDOP col-12-12"]//a[@class="VJA3rP"]/@href').extract()

    if product_detail_links:
      product_category = response.xpath('//*[@id="container"]/div/div[3]/div/div[1]/div/div[1]/div/div/section/div[3]/div/a/text()').extract_first()
      for link in product_detail_links:
        full_url = response.urljoin(link)  # Convert relative URL to absolute URL
        yield response.follow(full_url, callback=self.details_parse_product, meta={'product_category': product_category})
    
    else:

      product_name = response.xpath('//div[@class="cPHDOP col-12-12"]//div[@class="KzDlHZ"]/text()').extract()
      page_length = len(product_name)

      product_brand = [product.split()[0] for product in product_name]

      product_category = response.xpath('//*[@id="container"]/div/div[3]/div/div[1]/div/div[1]/div/div/section/div[3]/div/a/text()').extract_first()
      
      product_price = response.xpath('//div[@class="cPHDOP col-12-12"]//div[@class="Nx9bqj _4b5DiR"]/text()').extract()

      prod_description = []
      for i in range(1, page_length + 1):
        xpath_expr = f'//div[@class="cPHDOP col-12-12"][{i}]//div[@class="_6NESgJ"]//ul[@class="G4BRas"]//li/text()'
        prod_description.append(response.xpath(xpath_expr).extract())
      
      # print(len(product_name))
      # print(len(product_brand))
      # print(len(product_price))
      # print(len(prod_description))

      for record in range(page_length):
        try:
            yield {
                'Product Name': product_name[record] if record < len(product_name) else "Not Available",
                'Product Category': product_category,
                'Product Brand': product_brand[record] if record < len(product_brand) else "Not Available",
                'Product Price': product_price[record] if record < len(product_price) else "Not Available",
                'Product Description': prod_description[record] if record < len(prod_description) else "Not Available",
            }
        except IndexError:
            print(f"Error: Index out of range for record {record}")

      next_page = response.xpath("//a[span/text()='Next']/@href").get()
      if next_page:
          # Join the relative URL with the base URL of the current page
          next_page_url = response.urljoin(next_page)
          yield response.follow(next_page_url, self.parse)


  def details_parse_product(self, response):

    product_category = response.meta.get('product_category')

    product_name = response.xpath('//*[@id="container"]/div/div[3]/div[1]/div[2]/div[2]/div/div[1]/h1/span/text()').extract_first()

    product_brand = product_name.split()[0]

    product_price = response.xpath('//div[@class="cPHDOP col-12-12"]//div[@class="Nx9bqj CxhGGd"]/text()').extract_first()

    prod_description = ",".join(response.xpath('//div[@class="xFVion"]//ul/li/text()').extract())

    yield {
            'Product Name': product_name,
            'Product Category': product_category,
            'Product Brand': product_brand,
            'Product Price': product_price,
            'Product Description': prod_description,
          }
