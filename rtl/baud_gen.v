module baud_gen #(
    parameter CLKS_PER_BIT = 868          // 100 MHz / 115200 baud
) (
    input  wire clk,
    input  wire rst,
    output reg  tick                       // 1 for one cycle every CLKS_PER_BIT
);
    reg [$clog2(CLKS_PER_BIT)-1:0] cnt;

    always @(posedge clk) begin
        if (rst) begin
            cnt  <= 0;
            tick <= 1'b0;
        end else if (cnt == CLKS_PER_BIT - 1) begin
            cnt  <= 0;                     // restart counting
            tick <= 1'b1;                  // pulse!
        end else begin
            cnt  <= cnt + 1;
            tick <= 1'b0;
        end
    end
endmodule
