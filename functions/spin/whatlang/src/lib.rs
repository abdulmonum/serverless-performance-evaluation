use spin_sdk::http::{IntoResponse, Request, Response};
use spin_sdk::http_component;

use whatlang::detect;
use {std::collections::HashMap, url::Url};

fn parse_query_string(req: Request, parameter_name: &str) -> Result<String, String> {
    let full_url = req
        .header("spin-full-url")
        //.get("spin-full-url")
        .unwrap()
        .as_str()
        .unwrap();
    let parsed_url = Url::parse(full_url).or_else(|_e| {
        return Err("cannot parse the url...");
    });
    let hash_query: HashMap<_, _> = parsed_url.unwrap().query_pairs().into_owned().collect();
    let val = hash_query.get(parameter_name);
    if val.is_none() {
        return Err(
            format!("{parameter_name} parameter in the query string is missing...").to_string(),
        );
    }
    return Ok(val.unwrap().to_string());
}


/// A simple Spin HTTP component.
#[http_component]
fn handle_whatlang(req: Request) -> anyhow::Result<impl IntoResponse> {
    // println!("Handling request to {:?}", req.header("spin-full-url"));
    // Ok(Response::builder()
    //     .status(200)
    //     .header("content-type", "text/plain")
    //     .body("Hello, Fermyon")
    //     .build())
    match parse_query_string(req, "text") {
        Ok(v) => {
            let language = detect(&v).unwrap().lang();
            return Ok(Response::builder()
                .status(200)
                .header("content-type", "text/plain")
                .body(format!("<i>{v}</i> = <b>{language}</b>"))
                .build());
        }
        Err(e) => {
            return Ok(Response::builder()
                .status(500)
                .body(format!("{e}"))
                .build());
        }
    }
}
