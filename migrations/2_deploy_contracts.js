const Baseline = artifacts.require("Baseline")

module.exports = function (deployer) {
	deployer.deploy(Baseline)
		.then(() => {
			console.log('    > --------- For contract usage --------')
			console.log('    > Address: ' + Baseline.address)
			console.log('    > Stringify ABI: ' + JSON.stringify(Baseline.abi));
			console.log('    > -------------------------------------')
		})
}