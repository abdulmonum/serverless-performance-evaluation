use spin_sdk::http::{IntoResponse, Request, Response};
use spin_sdk::http_component;
use image::{ImageOutputFormat, GenericImageView, ImageFormat};
extern crate base64;
use serde_derive::{Deserialize, Serialize};

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct Input {
    input_image: String,
}

/// A simple Spin HTTP component.
#[http_component]
fn handle_imgthumbnail(req: Request) -> anyhow::Result<impl IntoResponse> {
    println!("Handling request to {:?}", req.header("spin-full-url"));
    let body = req.into_body();
    let input: Input = match serde_json::from_slice(&body) {
        Ok(input) => input,
        Err(e) => return Ok(Response::builder().status(500)
        .header("content-type", "text/plain")
        .body(format!("JSON decode error: {:?}", e))
        .build()),
    };
    let img_buf = match base64::decode(&input.input_image) {
        Ok(buf) => buf,
        Err(e) => return Ok(Response::builder().status(500)
        .header("content-type", "text/plain")
        .body(format!("Base64 decode error: {:?}", e))
        .build()),
    };

    println!("Image size in bytes: {}", img_buf.len());

    let img = match image::load_from_memory(&img_buf) {
        Ok(img) => img,
        Err(e) => return Ok(Response::builder().status(500)
        .header("content-type", "text/plain")
        .body(format!("Image load error: {:?}", e))
        .build()),
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
    Ok(Response::builder()
        .status(200)
        .header("content-type", "text/plain")
        .body(base64_string)
        .build())
}
