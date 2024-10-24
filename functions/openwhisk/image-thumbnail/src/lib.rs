extern crate serde_json;
extern crate base64;
use serde_derive::{Deserialize, Serialize};
use serde_json::{json, Error, Value};
use image::{ImageOutputFormat, GenericImageView, ImageFormat};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct Input {
    input_image: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct Output {
    output_image: String,
}

pub fn main(args: Value) -> Result<Value, Error> {

    let input: Input = match serde_json::from_value(args) {
        Ok(input) => input,
        Err(e) => return Ok(json!({ "error": format!("JSON decode error: {:?}", e) })),
    };
    
    let img_buf = match base64::decode(&input.input_image) {
        Ok(buf) => buf,
        Err(e) => return Ok(json!({ "error": format!("Base64 decode error: {:?}", e) })),
    };

    println!("Image size in bytes: {}", img_buf.len());

    let img = match image::load_from_memory(&img_buf) {
        Ok(img) => img,
        Err(e) => return Ok(json!({ "error": format!("Image load error: {:?}", e) })),
    };

    let (w,h) = img.dimensions();
    println!("Image size {} {}", w, h);
    println!("Drawing ...");
    let width_thumb: u32 = 100;
    let height_thumb: u32 = 100;
    let filtered = img.thumbnail(width_thumb, height_thumb);
    println!("Returning ...");
    let mut buf = vec![];

    let image_format_detected: ImageFormat = image::guess_format(&img_buf).unwrap();
    match image_format_detected {
        ImageFormat::Gif => {
            filtered.write_to(&mut buf, ImageOutputFormat::Gif).unwrap();

        },
        _ => {
            filtered.write_to(&mut buf, ImageOutputFormat::Png).unwrap();
        },
    }
    let base64_string = base64::encode(buf);

    let output = Output {
        output_image: base64_string,
    };

    serde_json::to_value(output)
    
}