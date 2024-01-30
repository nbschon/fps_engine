use fps_engine::run;

fn main() {
    println!("Hello, world!");
    pollster::block_on(run());
}
