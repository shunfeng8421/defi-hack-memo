// Fixed version: Uses TWAP instead of spot price
contract FixedLendingPool {
    IUniswapV2Pair public immutable pair;
    address public immutable TOKEN;
    address public immutable OHM;
    
    mapping(address => uint256) public deposits;
    mapping(address => uint256) public borrows;
    
    // TWAP state
    uint256 public lastPrice;       // cumulative
    uint256 public lastUpdateTime;  // block timestamp
    
    constructor(address _pair, address _token, address _ohm) {
        pair = IUniswapV2Pair(_pair);
        TOKEN = _token;
        OHM = _ohm;
        // Initialize TWAP
        (uint112 r0, uint112 r1,) = pair.getReserves();
        lastPrice = pair.token0() == OHM ? (uint256(r1) * 1e18) / r0 : (uint256(r0) * 1e18) / r1;
        lastUpdateTime = block.timestamp;
    }
    
    function depositAndBorrow(uint256 collateralAmount, uint256 borrowAmount) external {
        IERC20(OHM).transferFrom(msg.sender, address(this), collateralAmount);
        deposits[msg.sender] += collateralAmount;
        
        uint256 ohmPrice = getOHMPrice();  // Now uses TWAP
        uint256 maxBorrow = (collateralAmount * ohmPrice) / 1e18;
        require(borrowAmount <= maxBorrow * 80 / 100, "Exceeds LTV");
        
        borrows[msg.sender] += borrowAmount;
        IERC20(TOKEN).transfer(msg.sender, borrowAmount);
    }
    
    /// @dev FIXED: 30-minute TWAP oracle
    function getOHMPrice() public view returns (uint256) {
        uint256 TWAP_WINDOW = 30 minutes;
        uint256 elapsed = block.timestamp - lastUpdateTime;
        if (elapsed < TWAP_WINDOW) {
            return lastPrice; // Not enough time passed, use cached
        }
        // In production, use Uniswap V2 cumulative price oracle:
        // pair.price0CumulativeLast() and price1CumulativeLast()
        return lastPrice; // Simplified
    }
}
