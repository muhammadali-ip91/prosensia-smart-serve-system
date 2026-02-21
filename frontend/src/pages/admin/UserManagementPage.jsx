import { useState, useEffect } from 'react'
import adminApi from '../../api/adminApi'
import LoadingSpinner from '../../components/common/LoadingSpinner'
import Badge from '../../components/common/Badge'
import Modal from '../../components/common/Modal'
import toast from 'react-hot-toast'

export default function UserManagementPage() {
	const [users, setUsers] = useState([])
	const [loading, setLoading] = useState(true)
	const [roleFilter, setRoleFilter] = useState(null)
	const [showAddModal, setShowAddModal] = useState(false)
	const [showEditModal, setShowEditModal] = useState(false)
	const [addingUser, setAddingUser] = useState(false)
	const [editingUser, setEditingUser] = useState(false)
	const [selectedUserId, setSelectedUserId] = useState('')
	const [formData, setFormData] = useState({
		user_id: '',
		name: '',
		email: '',
		password: '',
		role: 'engineer',
		department: '',
		phone: '',
	})
	const [editFormData, setEditFormData] = useState({
		name: '',
		email: '',
		role: 'engineer',
		department: '',
		phone: '',
		password: '',
	})

	useEffect(() => { fetchUsers() }, [roleFilter])

	const fetchUsers = async () => {
		try {
			const data = await adminApi.getUsers(roleFilter)
			setUsers(data.users || [])
		} catch (error) { console.error(error) }
		finally { setLoading(false) }
	}

	const handleToggle = async (userId, currentActive) => {
		try {
			await adminApi.toggleUser(userId, !currentActive)
			toast.success(`User ${currentActive ? 'deactivated' : 'activated'}`)
			fetchUsers()
		} catch (error) { toast.error('Failed') }
	}

	const resetForm = () => {
		setFormData({
			user_id: '',
			name: '',
			email: '',
			password: '',
			role: 'engineer',
			department: '',
			phone: '',
		})
	}

	const handleAddUser = async () => {
		if (!formData.user_id || !formData.name || !formData.email || !formData.password || !formData.role) {
			toast.error('Please fill all required fields')
			return
		}

		setAddingUser(true)
		try {
			await adminApi.addUser(formData)
			toast.success('User created successfully')
			setShowAddModal(false)
			resetForm()
			fetchUsers()
		} catch (error) {
			const message = error?.response?.data?.detail?.message || 'Failed to create user'
			toast.error(message)
		} finally {
			setAddingUser(false)
		}
	}

	const openEditModal = (user) => {
		setSelectedUserId(user.user_id)
		setEditFormData({
			name: user.name || '',
			email: user.email || '',
			role: user.role || 'engineer',
			department: user.department || '',
			phone: user.phone || '',
			password: '',
		})
		setShowEditModal(true)
	}

	const handleUpdateUser = async () => {
		if (!selectedUserId || !editFormData.name || !editFormData.email || !editFormData.role) {
			toast.error('Please fill required fields')
			return
		}

		setEditingUser(true)
		try {
			const payload = {
				name: editFormData.name,
				email: editFormData.email,
				role: editFormData.role,
				department: editFormData.department || null,
				phone: editFormData.phone || null,
			}
			if (editFormData.password) {
				payload.password = editFormData.password
			}

			await adminApi.updateUser(selectedUserId, payload)
			toast.success('User updated successfully')
			setShowEditModal(false)
			setSelectedUserId('')
			fetchUsers()
		} catch (error) {
			const message = error?.response?.data?.detail?.message || 'Failed to update user'
			toast.error(message)
		} finally {
			setEditingUser(false)
		}
	}

	if (loading) return <LoadingSpinner size="lg" />

	return (
		<div className="page-container">
			<div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-6">
				<h1 className="page-title mb-0">User Management</h1>
				<button
					onClick={() => setShowAddModal(true)}
					className="btn-primary w-full sm:w-auto"
				>
					+ Add User
				</button>
			</div>

			{/* Filters */}
			<div className="flex flex-wrap gap-2 mb-6">
				{[null, 'engineer', 'kitchen', 'runner', 'admin'].map(role => (
					<button key={role || 'all'} onClick={() => setRoleFilter(role)}
						className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
							roleFilter === role ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
						}`}>
						{role ? role.charAt(0).toUpperCase() + role.slice(1) : 'All'}
					</button>
				))}
			</div>

			{/* Mobile Cards */}
			<div className="space-y-3 sm:hidden">
				{users.length === 0 ? (
					<div className="card text-center text-sm text-gray-500">No users found.</div>
				) : users.map(user => (
					<div key={user.user_id} className="card">
						<div className="flex items-start justify-between gap-3">
							<div>
								<p className="font-semibold text-gray-900">{user.name}</p>
								<p className="text-xs text-gray-500 font-mono break-all">{user.user_id}</p>
							</div>
							<Badge text={user.role} variant="primary" />
						</div>

						<p className="mt-2 text-sm text-gray-600 break-all">{user.email}</p>

						<div className="mt-3 flex items-center justify-between gap-2">
							<Badge text={user.is_active ? 'Active' : 'Inactive'} variant={user.is_active ? 'success' : 'danger'} />
							<button
								onClick={() => openEditModal(user)}
								className="text-sm font-medium text-primary-600 hover:text-primary-800"
							>
								Edit
							</button>
						</div>

						<button
							onClick={() => handleToggle(user.user_id, user.is_active)}
							className={`mt-3 w-full py-2 rounded-lg text-sm font-medium ${user.is_active ? 'text-red-600 bg-red-50 hover:bg-red-100' : 'text-green-600 bg-green-50 hover:bg-green-100'}`}
						>
							{user.is_active ? 'Deactivate' : 'Activate'}
						</button>
					</div>
				))}
			</div>

			{/* Desktop Table */}
			<div className="card table-scroll hidden sm:block">
				<table className="w-full text-sm">
					<thead>
						<tr className="border-b text-left text-gray-500">
							<th className="pb-3">ID</th><th className="pb-3">Name</th><th className="pb-3">Email</th>
							<th className="pb-3">Role</th><th className="pb-3">Status</th><th className="pb-3">Actions</th>
						</tr>
					</thead>
					<tbody>
						{users.map(user => (
							<tr key={user.user_id} className="border-b border-gray-50 hover:bg-gray-50">
								<td className="py-3 font-mono text-xs">{user.user_id}</td>
								<td className="py-3 font-medium">{user.name}</td>
								<td className="py-3 text-gray-500">{user.email}</td>
								<td className="py-3"><Badge text={user.role} variant="primary" /></td>
								<td className="py-3"><Badge text={user.is_active ? 'Active' : 'Inactive'} variant={user.is_active ? 'success' : 'danger'} /></td>
								<td className="py-3 whitespace-nowrap">
									<button onClick={() => openEditModal(user)}
										className="text-sm font-medium text-primary-600 hover:text-primary-800 mr-4">
										Edit
									</button>
									<button onClick={() => handleToggle(user.user_id, user.is_active)}
										className={`text-sm font-medium ${user.is_active ? 'text-red-500 hover:text-red-700' : 'text-green-500 hover:text-green-700'}`}>
										{user.is_active ? 'Deactivate' : 'Activate'}
									</button>
								</td>
							</tr>
						))}
					</tbody>
				</table>
			</div>

			<Modal isOpen={showAddModal} onClose={() => setShowAddModal(false)} title="Add New User">
				<div className="space-y-4">
					<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div>
							<label className="input-label">User ID *</label>
							<input
								className="input-field"
								value={formData.user_id}
								onChange={(e) => setFormData({ ...formData, user_id: e.target.value })}
								placeholder="ENG-011"
							/>
						</div>
						<div>
							<label className="input-label">Role *</label>
							<select
								className="input-field"
								value={formData.role}
								onChange={(e) => setFormData({ ...formData, role: e.target.value })}
							>
								<option value="engineer">Engineer</option>
								<option value="kitchen">Kitchen</option>
								<option value="runner">Runner</option>
								<option value="admin">Admin</option>
							</select>
						</div>
					</div>

					<div>
						<label className="input-label">Name *</label>
						<input
							className="input-field"
							value={formData.name}
							onChange={(e) => setFormData({ ...formData, name: e.target.value })}
							placeholder="Full Name"
						/>
					</div>

					<div>
						<label className="input-label">Email *</label>
						<input
							type="email"
							className="input-field"
							value={formData.email}
							onChange={(e) => setFormData({ ...formData, email: e.target.value })}
							placeholder="user@prosensia.com"
						/>
					</div>

					<div>
						<label className="input-label">Password *</label>
						<input
							type="password"
							className="input-field"
							value={formData.password}
							onChange={(e) => setFormData({ ...formData, password: e.target.value })}
							placeholder="Enter password"
						/>
					</div>

					<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div>
							<label className="input-label">Department</label>
							<input
								className="input-field"
								value={formData.department}
								onChange={(e) => setFormData({ ...formData, department: e.target.value })}
								placeholder="Production / Kitchen / Delivery"
							/>
						</div>
						<div>
							<label className="input-label">Phone</label>
							<input
								className="input-field"
								value={formData.phone}
								onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
								placeholder="03001234567"
							/>
						</div>
					</div>

					<div className="flex gap-3 pt-2">
						<button
							onClick={() => {
								setShowAddModal(false)
								resetForm()
							}}
							className="btn-secondary flex-1"
						>
							Cancel
						</button>
						<button
							onClick={handleAddUser}
							disabled={addingUser}
							className="btn-primary flex-1"
						>
							{addingUser ? 'Creating...' : 'Create User'}
						</button>
					</div>
				</div>
			</Modal>

			<Modal isOpen={showEditModal} onClose={() => setShowEditModal(false)} title="Edit User">
				<div className="space-y-4">
					<div>
						<label className="input-label">User ID</label>
						<input className="input-field bg-gray-100" value={selectedUserId} disabled />
					</div>

					<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div>
							<label className="input-label">Name *</label>
							<input
								className="input-field"
								value={editFormData.name}
								onChange={(e) => setEditFormData({ ...editFormData, name: e.target.value })}
							/>
						</div>
						<div>
							<label className="input-label">Role *</label>
							<select
								className="input-field"
								value={editFormData.role}
								onChange={(e) => setEditFormData({ ...editFormData, role: e.target.value })}
							>
								<option value="engineer">Engineer</option>
								<option value="kitchen">Kitchen</option>
								<option value="runner">Runner</option>
								<option value="admin">Admin</option>
							</select>
						</div>
					</div>

					<div>
						<label className="input-label">Email *</label>
						<input
							type="email"
							className="input-field"
							value={editFormData.email}
							onChange={(e) => setEditFormData({ ...editFormData, email: e.target.value })}
						/>
					</div>

					<div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
						<div>
							<label className="input-label">Department</label>
							<input
								className="input-field"
								value={editFormData.department}
								onChange={(e) => setEditFormData({ ...editFormData, department: e.target.value })}
							/>
						</div>
						<div>
							<label className="input-label">Phone</label>
							<input
								className="input-field"
								value={editFormData.phone}
								onChange={(e) => setEditFormData({ ...editFormData, phone: e.target.value })}
							/>
						</div>
					</div>

					<div>
						<label className="input-label">New Password (optional)</label>
						<input
							type="password"
							className="input-field"
							value={editFormData.password}
							onChange={(e) => setEditFormData({ ...editFormData, password: e.target.value })}
							placeholder="Leave empty to keep current password"
						/>
					</div>

					<div className="flex gap-3 pt-2">
						<button
							onClick={() => {
								setShowEditModal(false)
								setSelectedUserId('')
							}}
							className="btn-secondary flex-1"
						>
							Cancel
						</button>
						<button
							onClick={handleUpdateUser}
							disabled={editingUser}
							className="btn-primary flex-1"
						>
							{editingUser ? 'Saving...' : 'Save Changes'}
						</button>
					</div>
				</div>
			</Modal>
		</div>
	)
}
