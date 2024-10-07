CREATE TABLE "guests" (
  "id" integer PRIMARY KEY,
  "first_name" varchar,
  "last_name" varchar,
  "email" varchar,
  "address" varchar,
  "country" varchar,
  "city" varchar,
  "postcode" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "catalogs" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "description" text,
  "parent_id" integer,
  "level" integer,
  "sort_order" float,
  "image" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "products" (
  "id" integer PRIMARY KEY,
  "admin_id" integer,
  "sku" varchar,
  "code" varchar,
  "part_number" varchar,
  "name" varchar,
  "short_description" varchar,
  "description" text,
  "product_type" text,
  "catalog_id" integer,
  "promotion_id" integer,
  "image" varchar,
  "price" float,
  "member_price" float,
  "quantity" integer,
  "gallery" text,
  "weight" float,
  "diameter" float,
  "dimensions" varchar,
  "material" varchar,
  "label" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "promotions" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "description" text,
  "code" varchar,
  "from_date" date,
  "to_date" date,
  "special_price" float,
  "member_price" float,
  "rate" float,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "stores" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "phone_number" varchar,
  "email" varchar,
  "address" varchar,
  "postal_code" varchar,
  "opening_hours" datetime,
  "closing_hours" datetime,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "product_store" (
  "id" integer PRIMARY KEY,
  "store_id" integer,
  "product_id" integer,
  "quantity" integer
);

CREATE TABLE "orders" (
  "id" integer PRIMARY KEY,
  "transaction_number" varchar,
  "total_cost" float,
  "order_date" timestamp,
  "order_status" varchar,
  "gst_amount" float,
  "shipping_cost" float,
  "guest_id" integer,
  "location_pickup" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "order_details" (
  "id" integer PRIMARY KEY,
  "order_id" integer,
  "product_id" integer,
  "product_code" varchar,
  "product_name" varchar,
  "product_part_number" varchar,
  "quantity" integer,
  "unit_price" float,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "shippings" (
  "id" integer PRIMARY KEY,
  "order_id" integer,
  "product_id" integer,
  "name" varchar,
  "description" integer,
  "fee" float,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "payments" (
  "id" integer PRIMARY KEY,
  "guest_id" integer,
  "order_id" integer,
  "name" varchar,
  "description" integer,
  "credential" varchar,
  "image" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "transactions" (
  "id" integer PRIMARY KEY,
  "order_id" integer,
  "order_date" timestamp,
  "transaction_number" varchar,
  "amount" float,
  "bank_code" varchar,
  "bank_status" varchar,
  "bank_message" varchar,
  "created_at" timestamp
);

CREATE TABLE "admins" (
  "id" integer PRIMARY KEY,
  "user_name" varchar,
  "email" varchar,
  "password" varchar,
  "role" varchar,
  "azure_ad" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "blogs" (
  "id" integer PRIMARY KEY,
  "admin_id" integer,
  "title" varchar,
  "slug" varchar,
  "short_description" text,
  "content" text,
  "category_id" integer,
  "status" varchar,
  "image" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "categories" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "description" text,
  "image" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "tags" (
  "id" integer PRIMARY KEY,
  "name" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

CREATE TABLE "blog_tag" (
  "id" integer PRIMARY KEY,
  "blog_id" integer,
  "tag_id" integer,
  "created_at" timestamp
);

CREATE TABLE "settings" (
  "id" integer PRIMARY KEY,
  "key" varchar,
  "value" varchar,
  "created_at" timestamp,
  "updated_at" timestamp,
  "deleted_at" timestamp
);

COMMENT ON COLUMN "catalogs"."level" IS 'Nest level 0,1,2,...';

COMMENT ON COLUMN "catalogs"."sort_order" IS 'for Sorting';

COMMENT ON COLUMN "products"."quantity" IS 'Quantity of All store';

COMMENT ON COLUMN "products"."gallery" IS 'Array JSON';

COMMENT ON COLUMN "products"."label" IS 'New|Best seller|...';

COMMENT ON COLUMN "orders"."shipping_cost" IS 'certain value or free';

COMMENT ON COLUMN "orders"."guest_id" IS 'contains Guest info';

COMMENT ON COLUMN "payments"."credential" IS 'optional for third-party';

COMMENT ON COLUMN "blogs"."content" IS 'Content of the blog';

COMMENT ON COLUMN "blogs"."user_id" IS 'author';

COMMENT ON COLUMN "settings"."key" IS 'tax|delivery...';

ALTER TABLE "products" ADD FOREIGN KEY ("catalog_id") REFERENCES "catalogs" ("id");
ALTER TABLE "products" ADD FOREIGN KEY ("promotion_id") REFERENCES "promotions" ("id");
ALTER TABLE "products" ADD FOREIGN KEY ("admin_id") REFERENCES "admins" ("id");

ALTER TABLE "product_store" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("id");
ALTER TABLE "product_store" ADD FOREIGN KEY ("store_id") REFERENCES "stores" ("id");

ALTER TABLE "order_details" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id");
ALTER TABLE "order_details" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("id");

ALTER TABLE "orders" ADD FOREIGN KEY ("guest_id") REFERENCES "guests" ("id");

ALTER TABLE "transactions" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id");

ALTER TABLE "blogs" ADD FOREIGN KEY ("category_id") REFERENCES "categories" ("id");
ALTER TABLE "blogs" ADD FOREIGN KEY ("admin_id") REFERENCES "admins" ("id");

ALTER TABLE "blog_tag" ADD FOREIGN KEY ("blog_id") REFERENCES "blogs" ("id");
ALTER TABLE "blog_tag" ADD FOREIGN KEY ("tag_id") REFERENCES "tags" ("id");

ALTER TABLE "shippings" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id");
ALTER TABLE "shippings" ADD FOREIGN KEY ("product_id") REFERENCES "products" ("id");

ALTER TABLE "payments" ADD FOREIGN KEY ("order_id") REFERENCES "orders" ("id");
ALTER TABLE "payments" ADD FOREIGN KEY ("guest_id") REFERENCES "guests" ("id");


-- Bảng "guests":
-- Chức năng: Lưu trữ thông tin khách hàng (khách vãng lai).
-- Liên kết: Không có liên kết với các bảng khác trong hấp dẫn.
-- Bảng "catalogs":
-- Chức năng: Lưu trữ thông tin về danh mục sản phẩm.
-- Liên kết: Có khóa ngoại "catalog_id" liên kết với "id" trong bảng "products".
-- Bảng "products":
-- Chức năng: Lưu trữ thông tin về sản phẩm.
-- Liên kết:
-- Có khóa ngoại "catalog_id" liên kết với "id" trong bảng "catalogs".
-- Có khóa ngoại "promotion_id" liên kết với "id" trong bảng "promotions".
-- Bảng "promotions":
-- Chức năng: Lưu trữ thông tin về chương trình khuyến mãi.
-- Liên kết: Không có liên kết với các bảng khác trong hệ thống.
-- Bảng "stores":
-- Chức năng: Lưu trữ thông tin về cửa hàng.
-- Liên kết: Không có liên kết với các bảng khác trong hệ thống.
-- Bảng "product_store":
-- Chức năng: Liên kết sản phẩm với cửa hàng và số lượng sản phẩm có sẵn.
-- Liên kết:
-- Có khóa ngoại "product_id" liên kết với "id" trong bảng "products".
-- Có khóa ngoại "store_id" liên kết với "id" trong bảng "stores".
-- Bảng "orders":
-- Chức năng: Lưu trữ thông tin về đơn đặt hàng.
-- Liên kết:
-- Có khóa ngoại "guest_id" liên kết với "id" trong bảng "guests".
-- Bảng "order_details":
-- Chức năng: Lưu trữ thông tin chi tiết về đơn hàng.
-- Liên kết:
-- Có khóa ngoại "order_id" liên kết với "id" trong bảng "orders".
-- Có khóa ngoại "product_id" liên kết với "id" trong bảng "products".
-- Bảng "shippings":
-- Chức năng: Lưu trữ thông tin vận chuyển.
-- Liên kết: Không có liên kết với các bảng khác trong hệ thống.
-- Bảng "payments":
-- Chức năng: Lưu trữ thông tin về thanh toán.
-- Liên kết: Không có liên kết với các bảng khác trong hệ thống.
-- Bảng "transactions":
-- Chức năng: Lưu trữ thông tin giao dịch thanh toán.
-- Liên kết: Có khóa ngoại "order_id" liên kết với "id" trong bảng "orders".
-- Bảng "admins":
-- Chức năng: Lưu trữ thông tin về quản trị viên.
-- Liên kết: Không có liên kết với các bảng khác trong hệ thống.
-- Bảng "blogs":
-- Chức năng: Lưu trữ thông tin về bài viết trên blog.
-- Liên kết:
-- Có khóa ngoại "category_id" liên kết với "id" trong bảng "categories".
-- Có khóa ngoại "user_id" liên kết với "id" trong bảng "admins".
-- Bảng "categories":
-- Chức năng: Lưu trữ thông tin về danh mục trong blog.
-- Liên kết: Không có liên kết với các bảng khác trong hệ thống.
-- Bảng "tags":
-- Chức năng: Lưu trữ thông tin về các tag của bài viết blog.
-- Liên kết: Không có liên kết với các bảng khác trong hệ thống.
-- Bảng "blog_tag":
-- Chức năng: Liên kết giữa bài viết blog và tag.
-- Liên kết:
-- Có khóa ngoại "blog_id" liên kết với "id" trong bảng "blogs".
-- Có khóa ngoại "tag_id" liên kết với "id" trong bảng "tags".
-- Bảng "settings":
-- Chức năng: Lưu trữ các cài đặt hệ thống.
-- Liên kết: Không có liên kết với các bảng khác trong hệ thống.