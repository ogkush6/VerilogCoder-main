`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output logic reset,
	output logic s, w,
	input tb_match
);

	bit spulse_fail = 0;
	bit failed = 0;
	
	always @(posedge clk, negedge clk)
		if (!tb_match) failed = 1;
		
		
	initial begin
		reset <= 1;
		s <= 0;
		w <= 0;
		@(posedge clk);
		@(posedge clk);
		reset <= 0;
		@(posedge clk);
		@(posedge clk);
		
		s <= 1;

		repeat(200) @(posedge clk, negedge clk) begin
			w <= $random;
		end

		reset <= 1;
		@(posedge clk);
		reset <= 0;
		@(posedge clk);
		@(posedge clk);

		repeat(200) @(posedge clk, negedge clk) begin
			w <= $random;
		end
		
		@(posedge clk)		
			spulse_fail <= failed;
		
		repeat(500) @(negedge clk) begin
			reset <= !($random & 63);
			s <= !($random & 7);
			w <= $random;
		end

		if (failed && !spulse_fail) begin
			$display ("Hint: Your state machine should ignore input 's' after the state A to B transition.");
		end
		
		#1 $finish;
	end
	
endmodule

module tb();

	typedef struct packed {
		int errors;
		int errortime;
		int errors_z;
		int errortime_z;

		int clocks;
	} stats;
	
	stats stats1;
	
	
	wire[511:0] wavedrom_title;
	wire wavedrom_enable;
	int wavedrom_hide_after_time;
	
	reg clk=0;
	initial forever
		#5 clk = ~clk;

	logic reset;
	logic s;
	logic w;
	logic z_ref;
	logic z_dut;

	initial begin 
		$dumpfile("wave.vcd");
		$dumpvars();
	end


	wire tb_match;		// Verification
	wire tb_mismatch = ~tb_match;
	
	stimulus_gen stim1 (
		.clk,
		.* ,
		.reset,
		.s,
		.w );
	RefModule good1 (
		.clk,
		.reset,
		.s,
		.w,
		.z(z_ref) );
		
	TopModule top_module1 (
		.clk,
		.reset,
		.s,
		.w,
		.z(z_dut) );

	
	bit strobe = 0;
	task wait_for_end_of_timestep;
		repeat(5) begin
			strobe <= !strobe;  // Try to delay until the very end of the time step.
			@(strobe);
		end
	endtask	

	
	final begin
		if (stats1.errors_z) $display("Hint: Output '%s' has %0d mismatches. First mismatch occurred at time %0d.", "z", stats1.errors_z, stats1.errortime_z);
		else $display("Hint: Output '%s' has no mismatches.", "z");

		$display("Hint: Total mismatched samples is %1d out of %1d samples\n", stats1.errors, stats1.clocks);
		$display("Simulation finished at %0d ps", $time);
		$display("Mismatches: %1d in %1d samples", stats1.errors, stats1.clocks);
	end
	
	// Verification: XORs on the right makes any X in good_vector match anything, but X in dut_vector will only match X.
	assign tb_match = ( { z_ref } === ( { z_ref } ^ { z_dut } ^ { z_ref } ) );
	// Use explicit sensitivity list here. @(*) causes NetProc::nex_input() to be called when trying to compute
	// the sensitivity list of the @(strobe) process, which isn't implemented.
	always @(posedge clk, negedge clk) begin

		stats1.clocks++;
		if (!tb_match) begin
			if (stats1.errors == 0) stats1.errortime = $time;
			stats1.errors++;
		end
		if (z_ref !== ( z_ref ^ z_dut ^ z_ref ))
		begin if (stats1.errors_z == 0) stats1.errortime_z = $time;
			stats1.errors_z = stats1.errors_z+1'b1; end

	end

   // add timeout after 100K cycles
   initial begin
     #1000000
     $display("TIMEOUT");
     $finish();
   end

endmodule



module RefModule (
  input clk,
  input reset,
  input s,
  input w,
  output reg z
);

  parameter A=0, B=1, C=2, S10=3, S11=4, S20=5, S21=6, S22=7;
  reg [2:0] state, next;

  always @(posedge clk) begin
    if (reset) state <= A;
    else state <= next;
  end

  always_comb begin
    case (state)
      A: next = s ? B : A;
      B: next = w ? S11 : S10;
      C: next = w ? S11 : S10;
      S10: next = w ? S21 : S20;
      S11: next = w ? S22 : S21;
      S20: next = B;
      S21: next = w ? C : B;
      S22: next = w ? B : C;
      default: next = 'x;
    endcase
  end

  assign z = (state == C);

endmodule


module TopModule (
    input  logic clk,
    input  logic reset,
    input  logic s,
    input  logic w,
    output logic z
);

    // State encoding
    localparam STATE_A  = 3'b000;
    localparam STATE_B  = 3'b001;
    localparam STATE_B1 = 3'b010;
    localparam STATE_B2 = 3'b011;
    localparam STATE_Z  = 3'b100;

    // State register
    logic [2:0] state;
    logic [2:0] state_next;

    // Previous w values
    logic pre_w, pre_pre_w;

    always @(posedge clk) begin
        if (reset) begin
            state <= STATE_A;
            pre_w <= 0;
            pre_pre_w <= 0;
        end else begin
            state <= state_next;
            pre_pre_w <= pre_w;
            pre_w <= w;
        end
    end

    // State transition logic
    always @(*) begin
        state_next = state; // Default to hold current state
        case (state)
            STATE_A: begin
                if (s == 1) begin
                    state_next = STATE_B;
                end else begin
                    state_next = STATE_A;
                end
            end
            STATE_B: begin
                state_next = STATE_B1;
            end
            STATE_B1: begin
                state_next = STATE_B2;
            end
            STATE_B2: begin
                if ((pre_pre_w & pre_w & !w) || (pre_pre_w & !pre_w & w) || (!pre_pre_w & pre_w & w)) begin
                    state_next = STATE_Z;
                end else begin
                    state_next = STATE_B;
                end
            end
            STATE_Z: begin
                state_next = STATE_B1;
            end
        endcase
    end

    // Output logic
    always @(*) begin
        z = (state == STATE_Z);
    end

endmodule