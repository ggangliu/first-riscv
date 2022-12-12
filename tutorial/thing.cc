#include <backends/cxxrtl/cxxrtl.h>

#if defined(CXXRTL_INCLUDE_CAPI_IMPL) || \
    defined(CXXRTL_INCLUDE_VCD_CAPI_IMPL)
#include <backends/cxxrtl/cxxrtl_capi.cc>
#endif

#if defined(CXXRTL_INCLUDE_VCD_CAPI_IMPL)
#include <backends/cxxrtl/cxxrtl_vcd_capi.cc>
#endif

using namespace cxxrtl_yosys;

namespace cxxrtl_design {

// \amaranth.hierarchy: top
// \top: 1
// \generator: Amaranth
struct p_top : public module {
	// \src: elaborate_main.py:9
	/*input*/ value<1> p_rst;
	// \src: elaborate_main.py:9
	/*input*/ value<1> p_clk;
	p_top() {}
	p_top(adopt, p_top other) {}

	void reset() override {
		*this = p_top(adopt {}, std::move(*this));
	}

	bool eval() override;
	bool commit() override;

	void debug_eval();

	void debug_info(debug_items &items, std::string path = "") override;
}; // struct p_top

bool p_top::eval() {
	bool converged = true;
	return converged;
}

bool p_top::commit() {
	bool changed = false;
	return changed;
}

void p_top::debug_eval() {
}

CXXRTL_EXTREMELY_COLD
void p_top::debug_info(debug_items &items, std::string path) {
	assert(path.empty() || path[path.size() - 1] == ' ');
	items.add(path + "rst", debug_item(p_rst, 0, debug_item::INPUT|debug_item::UNDRIVEN));
	items.add(path + "clk", debug_item(p_clk, 0, debug_item::INPUT|debug_item::UNDRIVEN));
}

} // namespace cxxrtl_design

extern "C"
cxxrtl_toplevel cxxrtl_design_create() {
	return new _cxxrtl_toplevel { std::unique_ptr<cxxrtl_design::p_top>(new cxxrtl_design::p_top) };
}

