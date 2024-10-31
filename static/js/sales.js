document.addEventListener('DOMContentLoaded', function() {
    loadBranches();
    const saleDate = document.getElementById('saleDate');
    const branchSelect = document.getElementById('branchSelect');
    const submitButton = document.getElementById('submitSalesButton');

    // 지점 선택 시 버튼 상태 업데이트
    branchSelect.addEventListener('change', function() {
        updateSubmitButtonState();
    });

    // 날짜와 지점 선택에 따른 제출 버튼 상태 업데이트
    [saleDate, branchSelect].forEach(item => {
        item.addEventListener('change', updateSubmitButtonState);
    });

    // 초기 버튼 상태 설정
    updateSubmitButtonState();

    // 폼 제출 시 이벤트 핸들러
    document.getElementById('salesForm').addEventListener('submit', function(event) {
        event.preventDefault();  // 기본 폼 제출 방지
        showConfirmationModal(); // 모달 보여주기
    });

    // 모달에서 확인 버튼 클릭 시 폼 제출
    document.getElementById('confirmSubmit').addEventListener('click', function() {
        document.getElementById('salesForm').submit();  // 확인 버튼 클릭 시 폼 제출
    });
});

// 지점 목록을 로드하여 드롭다운에 추가
function loadBranches() {
    fetch('/api/branches')
        .then(response => response.json())
        .then(branches => {
            const branchSelect = document.getElementById('branchSelect');
            branchSelect.innerHTML = '<option disabled selected value="">지점 선택</option>';
            branches.forEach(branch => {
                const option = new Option(branch.name, branch.id);
                branchSelect.add(option);
            });
        })
        .catch(error => console.log('Error loading branches:', error));
}

// 제출 버튼 활성화/비활성화
function updateSubmitButtonState() {
    const saleDate = document.getElementById('saleDate').value;
    const branchId = document.getElementById('branchSelect').value;
    const submitButton = document.getElementById('submitSalesButton');
    submitButton.disabled = !saleDate || !branchId;
}

// 매출 정보를 팝업에 표시
function showConfirmationModal() {
    document.getElementById('confirmSaleDate').innerText = document.getElementById('saleDate').value;
    document.getElementById('confirmBranch').innerText = document.getElementById('branchSelect').options[document.getElementById('branchSelect').selectedIndex].text;
    document.getElementById('confirmSalesCardSweetdream').innerText = document.getElementById('salesCardSweetdream').value || '0';
    document.getElementById('confirmSalesCash').innerText = document.getElementById('salesCash').value || '0';
    document.getElementById('confirmSalesZeropay').innerText = document.getElementById('salesZeropay').value || '0';
    document.getElementById('confirmSalesTransfer').innerText = document.getElementById('salesTransfer').value || '0';

    // 부트스트랩 모달 표시
    $('#confirmationModal').modal('show');
}