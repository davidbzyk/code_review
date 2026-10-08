use std::collections::HashMap;

/// Add two numbers.
pub fn add(a: i32, b: i32) -> i32 {
    let total = a + b;
    total
}

#[derive(Debug)]
pub struct Counter {
    pub hits: HashMap<String, u32>,
}

impl Counter {
    pub fn new() -> Self {
        Counter { hits: HashMap::new() }
    }

    pub fn bump(&mut self, key: &str) -> u32 {
        let slot = self.hits.entry(key.to_string()).or_insert(0);
        *slot += 1;
        *slot
    }
}

pub fn describe(counter: &Counter) -> String {
    format!("{} keys", counter.hits.len())
}
