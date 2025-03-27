`timescale 1 ps/1 ps
`define OK 12
`define INCORRECT 13


module stimulus_gen (
	input clk,
	output logic reset,
	output logic x
);

	initial begin
		reset = 1;
		x = 0;
		@(posedge clk);
		@(posedge clk);
		reset = 0;
		@(posedge clk);
		@(posedge clk);
		
		repeat(500) @(negedge clk) begin
			reset <= !($random & 63);
			x <= $random;
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
	logic x;
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
		.x );
	RefModule good1 (
		.clk,
		.reset,
		.x,
		.z(z_ref) );
		
	TopModule top_module1 (
		.clk,
		.reset,
		.x,
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
  input x,
  output reg z
);

  parameter A=0, B=1, C=2, D=3, E=4;
  reg [2:0] state, next;

  always @(posedge clk) begin
    if (reset) state <= A;
    else state <= next;
  end

  always_comb begin
    case (state)
      A: next = x ? B : A;
      B: next = x ? E : B;
      C: next = x ? B : C;
      D: next = x ? C : B;
      E: next = x ? E : D;
      default: next = 'x;
    endcase
  end

  assign z = (state == D) || (state == E);

endmodule


module TopModule
(
  input  logic clk,
  input  logic reset,
  input  logic x,
  output logic z
);

  // State enum
  localparam STATE_0 = 3'b000;
  localparam STATE_1 = 3'b001;
  localparam STATE_2 = 3'b010;
  localparam STATE_3 = 3'b011;
  localparam STATE_4 = 3'b100;

  // State register
  logic [2:0] state;
  logic [2:0] state_next;

  always @(posedge clk) begin
    if ( reset )
      state <= STATE_0;
    else
      state <= state_next;
  end

  // Next state combinational logic
  always @(*) begin
    case ( state )
      STATE_0: state_next = ( x ) ? STATE_1 : STATE_0;
      STATE_1: state_next = ( x ) ? STATE_4 : STATE_1;
      STATE_2: state_next = ( x ) ? STATE_1 : STATE_2;
      STATE_3: state_next = ( x ) ? STATE_2 : STATE_1;
      STATE_4: state_next = ( x ) ? STATE_4 : STATE_3;
    endcase
  end

  // Output combinational logic
  always @(*) begin
    case ( state )
      STATE_0: z = 1'b0;
      STATE_1: z = 1'b0;
      STATE_2: z = 1'b0;
      STATE_3: z = 1'b1;
      STATE_4: z = 1'b1;
    endcase
  end

endmodule