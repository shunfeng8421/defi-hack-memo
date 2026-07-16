// 审计任务: 找出这个合约的漏洞
// 这是一个简化版的借贷协议

pragma solidity ^0.8.0;

interface IERC20 {
    function transferFrom(address, address, uint) external returns (bool);
    function balanceOf(address) external view returns (uint);
}

interface IUniswapV2Pair {
    function getReserves() external view returns (uint112, uint112, uint32);
    function token0() external view returns (address);
    function token1() external view returns (address);
}

contract SimpleLender {
    IERC20 public tokenA;
    IERC20 public tokenB;
    IUniswapV2Pair public pair;

    mapping(address => uint) public deposits;
    mapping(address => uint) public borrows;

    constructor(address _tokenA, address _tokenB, address _pair) {
        tokenA = IERC20(_tokenA);
        tokenB = IERC20(_tokenB);
        pair = IUniswapV2Pair(_pair);
    }

    // 用户存入 tokenA 作为抵押品
    function deposit(uint amount) external {
        tokenA.transferFrom(msg.sender, address(this), amount);
        deposits[msg.sender] += amount;
    }

    // 获取 tokenA 的当前价格 (相对于 tokenB)
    function getPrice() public view returns (uint) {
        (uint reserve0, uint reserve1, ) = pair.getReserves();
        if (pair.token0() == address(tokenA)) {
            return reserve1 * 1e18 / reserve0;
        } else {
            return reserve0 * 1e18 / reserve1;
        }
    }

    // 用户可借出 tokenB, 最高为抵押品价值的 75%
    function borrow(uint amountB) external {
        uint price = getPrice();
        uint maxBorrow = deposits[msg.sender] * price * 75 / 100 / 1e18;
        require(borrows[msg.sender] + amountB <= maxBorrow, "超过借款上限");

        borrows[msg.sender] += amountB;
        tokenB.transfer(msg.sender, amountB);
    }

    // 还款
    function repay(uint amountB) external {
        tokenB.transferFrom(msg.sender, address(this), amountB);
        borrows[msg.sender] -= amountB;
    }

    // 提现抵押品 (必须先还清借款)
    function withdraw(uint amountA) external {
        require(borrows[msg.sender] == 0, "还有未还借款");
        require(deposits[msg.sender] >= amountA, "余额不足");
        deposits[msg.sender] -= amountA;
        tokenA.transfer(msg.sender, amountA);
    }
}
