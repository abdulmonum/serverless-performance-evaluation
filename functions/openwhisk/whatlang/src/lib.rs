extern crate whatlang;
extern crate serde_json;
use whatlang::detect;
use serde_derive::{Deserialize, Serialize};
use serde_json::{Error, Value};


#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct Input {
    sentence: String,
}

#[derive(Debug, Clone, PartialEq, Serialize, Deserialize)]
struct Output {
    greeting: String,
}




pub fn main(args: Value) -> Result<Value, Error> {
    //let input: Input = serde_json::from_value(args)?;
    let sentence = "The quick brown fox jumps over the lazy dog";
    let language = detect(&sentence).unwrap().lang();
    let output = Output {
        greeting: format!("<i>{sentence}</i> = <b>{language}</b>"),
    };
    serde_json::to_value(output)
}